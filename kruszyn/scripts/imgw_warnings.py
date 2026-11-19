#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pobiera ostrzeżenia meteorologiczne IMGW dla powiatu bolesławieckiego.

Użycie (z głównego folderu repozytorium):
  python3 scripts/imgw_warnings.py              # -> ostrzezenia.json
  python3 scripts/imgw_warnings.py --discover   # pokaż pierwsze surowe wpisy (diagnostyka)
  python3 scripts/imgw_warnings.py --selftest

Źródło: publiczne API IMGW https://danepubliczne.imgw.pl/api/data/warningsmeteo
(lista ostrzeżeń, każde ma listę kodów TERYT powiatów, których dotyczy).
Powiat bolesławiecki = TERYT 0201. Przy błędzie skrypt NIE nadpisuje istniejącego pliku.
"""
import argparse
import datetime as dt
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

URL = "https://danepubliczne.imgw.pl/api/data/warningsmeteo"
POWIAT = "0201"
OUT = Path("ostrzezenia.json")
TZ = ZoneInfo("Europe/Warsaw")
UA = {"User-Agent": "kruszyn-wies-app/1.0 (aplikacja mieszkancow wsi)", "Accept": "application/json"}


def fetch():
    """Pobiera listę ostrzeżeń. IMGW zwraca HTTP 404 (zamiast pustej listy), gdy nie ma żadnych
    aktywnych ostrzeżeń w kraju – to normalna sytuacja, traktujemy ją jako pustą listę."""
    req = urllib.request.Request(URL, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode("utf-8")
            print(f"IMGW: HTTP {r.status}, {len(body)} znaków")
            data = json.loads(body)
            # Brak ostrzeżeń w kraju: IMGW zwraca {"message": "Brak ostrzeżeń meteorologicznych"} (HTTP 200)
            if isinstance(data, dict) and set(data) == {"message"} and "brak" in str(data["message"]).lower():
                print("IMGW: " + str(data["message"]))
                return []
            return data
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("IMGW: HTTP 404 = brak aktywnych ostrzeżeń w kraju")
            return []
        raise SystemExit(f"IMGW: błąd HTTP {e.code} {e.reason}")
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        raise SystemExit(f"IMGW: nie udało się pobrać lub odczytać odpowiedzi: {e!r}")


def local(ts):
    """Tekst z IMGW -> 'YYYY-MM-DDTHH:MM' w czasie polskim (brak strefy = czas polski)."""
    if not ts:
        return None
    d = dt.datetime.fromisoformat(str(ts).strip().replace("Z", "+00:00").replace(" ", "T", 1))
    d = d.replace(tzinfo=TZ) if d.tzinfo is None else d.astimezone(TZ)
    return d.strftime("%Y-%m-%dT%H:%M")


def first(d, *keys):
    for k in keys:
        if d.get(k) not in (None, ""):
            return d[k]
    return None


def covers(item):
    t = item.get("teryt")
    if isinstance(t, str):
        t = [x.strip() for x in t.replace(";", ",").split(",")]
    return any(str(x).strip()[:4] == POWIAT for x in (t or []))


def parse(raw, now=None):
    if not isinstance(raw, list):
        raise ValueError("odpowiedź nie jest listą")
    now_s = (now or dt.datetime.now(TZ)).strftime("%Y-%m-%dT%H:%M")
    items, mine = [], 0
    for it in raw:
        if not isinstance(it, dict) or not covers(it):
            continue
        mine += 1
        name = first(it, "nazwa_zdarzenia", "zdarzenie", "nazwa")
        if not name:
            print("Uwaga: wpis bez nazwy zdarzenia, pola:", sorted(it.keys()))
            name = "Ostrzeżenie meteorologiczne"
        od, do = local(first(it, "obowiazuje_od", "od")), local(first(it, "obowiazuje_do", "do"))
        if do and do < now_s:
            continue
        try:
            stopien = int(str(first(it, "stopien", "stopień") or 0)[:1])
        except ValueError:
            stopien = 0
        items.append({
            "id": first(it, "id"), "zdarzenie": str(name).strip(), "stopien": stopien,
            "prawdopodobienstwo": first(it, "prawdopodobienstwo"),
            "od": od, "do": do,
            "tresc": (first(it, "tresc") or "").strip(),
            "komentarz": (first(it, "komentarz") or "").strip(),
        })
    items.sort(key=lambda x: (-x["stopien"], x["od"] or ""))
    return items


def selftest():
    now = dt.datetime(2026, 11, 16, 7, 0, tzinfo=TZ)
    raw = [
        {"id": 1, "nazwa_zdarzenia": "Silny wiatr", "stopien": "2", "prawdopodobienstwo": "80",
         "obowiazuje_od": "2026-11-16 12:00:00", "obowiazuje_do": "2026-11-17 06:00:00",
         "tresc": "Wiatr do 80 km/h.", "teryt": ["0201", "0202"]},
        {"id": 2, "nazwa_zdarzenia": "Mróz", "stopien": "1", "obowiazuje_od": "2026-11-18 00:00:00",
         "obowiazuje_do": "2026-11-19 09:00:00", "teryt": ["0201"]},
        {"id": 3, "nazwa_zdarzenia": "Burze", "stopien": "3", "obowiazuje_od": "2026-11-16 12:00:00",
         "obowiazuje_do": "2026-11-17 06:00:00", "teryt": ["1465"]},
        {"id": 4, "nazwa_zdarzenia": "Stare", "stopien": "1", "obowiazuje_od": "2026-11-10 00:00:00",
         "obowiazuje_do": "2026-11-11 00:00:00", "teryt": ["0201"]},
    ]
    r = parse(raw, now)
    assert [x["zdarzenie"] for x in r] == ["Silny wiatr", "Mróz"], r
    assert r[0]["stopien"] == 2 and r[0]["do"] == "2026-11-17T06:00"
    assert parse([], now) == []
    assert parse([{"teryt": ["0201"], "stopien": "1"}], now)[0]["zdarzenie"] == "Ostrzeżenie meteorologiczne"
    print("selftest OK")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--discover", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    raw = fetch()
    if a.discover:
        print(json.dumps(raw[:3] if isinstance(raw, list) else raw, ensure_ascii=False, indent=1)[:4000])
    if isinstance(raw, list):
        mine = sum(1 for it in raw if isinstance(it, dict) and covers(it))
        print(f"IMGW zwróciło {len(raw)} ostrzeżeń dla całego kraju; dla powiatu {POWIAT}: {mine}")
        if raw and not mine:
            sample = sorted({str(x)[:4] for it in raw if isinstance(it, dict) for x in (it.get("teryt") or [])})[:8]
            print("Przykładowe kody TERYT w odpowiedzi:", sample, "| pola pierwszego wpisu:", sorted(raw[0].keys()) if isinstance(raw[0], dict) else type(raw[0]).__name__)
    else:
        print("Nieoczekiwany typ odpowiedzi IMGW:", type(raw).__name__, repr(raw)[:300])
    try:
        items = parse(raw)
    except ValueError as e:
        raise SystemExit(f"Błąd odpowiedzi IMGW: {e}")
    now = dt.datetime.now(dt.timezone.utc)
    OUT.write_text(json.dumps({"updated": now.isoformat(timespec="seconds"), "source": "https://meteo.imgw.pl/",
                               "items": items}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Zapisano {OUT}: {len(items)} ostrzeżeń")


if __name__ == "__main__":
    sys.exit(main())
