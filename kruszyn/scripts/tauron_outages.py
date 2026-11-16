#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pobiera wyłączenia prądu dla Kruszyna z publicznego API Tauron Dystrybucja.

Użycie (z głównego folderu repozytorium):
  python3 scripts/tauron_outages.py              # normalna praca -> wylaczenia.json
  python3 scripts/tauron_outages.py --discover   # pokaż surowe odpowiedzi (diagnostyka)
  python3 scripts/tauron_outages.py --selftest

Jak to działa:
  1. Przy pierwszym uruchomieniu szuka miejscowości i ulicy w słownikach Tauron
     i zapisuje ich identyfikatory w data/tauron_config.json.
  2. Pyta o wyłączenia na najbliższe 30 dni.
  3. Zostawia tylko te, w których tekście jest nazwa wsi (KEYWORDS), bo dla wsi
     Tauron zwraca wyłączenia z całej okolicy.
Gdy cokolwiek pójdzie nie tak, skrypt kończy się błędem i NIE nadpisuje
istniejącego wylaczenia.json.

Dane są publiczne i dostępne bez logowania, ale to nie jest oficjalne, gwarantowane API,
więc nazwy pól mogą się zmienić. Dlatego skrypt jest ostrożny. Odpytuj je rzadko (raz na godzinę).
"""
import argparse
import datetime as dt
import json
import sys
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

BASE = "https://www.tauron-dystrybucja.pl"
CITIES = "/waapi/enum/geo/cities"
STREETS = "/waapi/enum/geo/streets"
OUTAGES = "/waapi/outages/address"

CITY = "Kruszyn"
AREA_HINTS = ["Bolesławiec"]          # gmina/powiat do odróżnienia od innych Kruszynów
KEYWORDS = ["Kruszyn"]                # słowa w treści komunikatu, które uznajemy za „nasze”
HOUSE_NO = "1"
LOOKAHEAD_DAYS = 30

CONFIG = Path("data/tauron_config.json")
OUT = Path("wylaczenia.json")
TZ = ZoneInfo("Europe/Warsaw")
UA = {"User-Agent": "kruszyn-wies-app/1.0 (aplikacja mieszkancow wsi)",
      "Accept": "application/json"}


def get(endpoint, params):
    url = BASE + endpoint + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    return s


def flat_text(d):
    return " ".join(str(v) for v in d.values() if isinstance(v, (str, int)))


def discover():
    """Znajdź identyfikatory miejscowości i ulicy (lub użyj zapisanych)."""
    if CONFIG.exists():
        c = json.loads(CONFIG.read_text(encoding="utf-8"))
        if c.get("city_gaid") and c.get("street_gaid"):
            return c
    cities = get(CITIES, {"partName": CITY})
    if not isinstance(cities, list):
        raise SystemExit("Nieoczekiwana odpowiedź słownika miejscowości: " + repr(cities)[:300])
    cand = [c for c in cities if norm(c.get("Name", "")) == norm(CITY)]
    hinted = [c for c in cand if any(norm(h) in norm(flat_text(c)) for h in AREA_HINTS)]
    if not hinted:
        raise SystemExit(f"Nie rozpoznano miejscowości {CITY} (okolice: {AREA_HINTS}). "
                         f"Kandydaci: {json.dumps(cand, ensure_ascii=False)[:800]}")
    city = hinted[0]
    gaid = city["GAID"]
    street, how = None, "lista ulic"
    for part in (CITY, CITY[:3], "ul.", "Gł", "Pol", "Lip"):   # wieś bez ulic często nie ma żadnej na liście
        if len(part) < 3:
            continue
        streets = get(STREETS, {"partName": part, "ownerGAID": gaid})
        n = len(streets) if isinstance(streets, list) else repr(streets)[:80]
        print(f"Ulice dla '{part}': {n}")
        if isinstance(streets, list) and streets:
            street = streets[0]
            break
    if not street:
        # wieś bez ulic: Tauron używa wtedy numeru miejscowości także jako numeru "ulicy"
        street, how = {"Name": CITY, "GAID": gaid}, "numer miejscowości zamiast ulicy"
    print(f"Miejscowość: {city.get('Name')} (GAID {gaid}); ulica: {street.get('Name')} (GAID {street['GAID']}) – {how}")
    return {"city": city.get("Name"), "city_gaid": gaid,
            "street": street.get("Name"), "street_gaid": street["GAID"], "house_no": HOUSE_NO}


def save_config(cfg):
    CONFIG.parent.mkdir(exist_ok=True)
    CONFIG.write_text(json.dumps(cfg, ensure_ascii=False, indent=1), encoding="utf-8")
    print("Zapisano konfigurację:", cfg)


def local(ts):
    """'2026-09-28T07:00:00Z' -> '2026-09-28T09:00' (czas polski)."""
    if not ts:
        return None
    d = dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    if d.tzinfo is None:
        d = d.replace(tzinfo=dt.timezone.utc)
    return d.astimezone(TZ).strftime("%Y-%m-%dT%H:%M")


def parse(raw, keywords=KEYWORDS):
    """Odpowiedź API -> lista wpisów dla aplikacji."""
    if not isinstance(raw, dict):
        raise ValueError("odpowiedź nie jest obiektem")
    if raw.get("IdsWWW") == [0]:
        raise ValueError("Tauron nie obsługuje tego obszaru")
    point = raw.get("AddressPoint") if isinstance(raw.get("AddressPoint"), dict) else {}
    pid = point.get("AddressPointId")
    exact = raw.get("OutageListType") == 1
    items, seen = [], set()
    for it in raw.get("OutageItems") or []:
        text = (it.get("Message") or "").strip()
        mine = exact or (pid is not None and pid in (it.get("AddressPointIds") or [])) \
            or any(norm(k) in norm(text) for k in keywords)
        if not mine:
            continue
        # TypeId: 1 = planowane, 2 = awaria
        typ = "awaria" if it.get("TypeId") == 2 else "planowane"
        if typ == "awaria" and not it.get("IsActive"):
            continue
        key = (it.get("OutageId"), it.get("StartDate"))
        if key in seen:
            continue
        seen.add(key)
        items.append({"typ": typ, "od": local(it.get("StartDate")), "do": local(it.get("EndDate")), "tekst": text})
    items.sort(key=lambda x: x["od"] or "")
    return items


def selftest():
    sample = {"OutageListType": 2, "AddressPoint": {"AddressPointId": 5},
              "OutageItems": [
                  {"OutageId": "a", "StartDate": "2026-12-03T07:00:00Z", "EndDate": "2026-12-03T13:00:00Z",
                   "TypeId": 1, "IsActive": True, "Message": "Kruszyn, Łaziska 1-20.", "AddressPointIds": []},
                  {"OutageId": "b", "StartDate": "2026-12-04T07:00:00Z", "EndDate": "2026-12-04T11:00:00Z",
                   "TypeId": 1, "IsActive": True, "Message": "Inna wieś 1.", "AddressPointIds": []},
                  {"OutageId": "c", "StartDate": "2026-12-05T07:00:00Z", "EndDate": "2026-12-05T11:00:00Z",
                   "TypeId": 2, "IsActive": True, "Message": "Zwarcie", "AddressPointIds": [5]},
                  {"OutageId": "d", "StartDate": "2026-12-06T07:00:00Z", "EndDate": "2026-12-06T11:00:00Z",
                   "TypeId": 2, "IsActive": False, "Message": "Kruszyn stara awaria", "AddressPointIds": [5]},
              ]}
    r = parse(sample)
    assert [x["tekst"] for x in r] == ["Kruszyn, Łaziska 1-20.", "Zwarcie"], r
    assert r[0]["od"] == "2026-12-03T08:00" and r[0]["do"] == "2026-12-03T14:00", r[0]
    assert r[1]["typ"] == "awaria"
    try:
        parse({"IdsWWW": [0]})
        raise AssertionError("powinien być błąd")
    except ValueError:
        pass
    print("selftest OK")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--discover", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    cfg = discover()
    cached = CONFIG.exists()
    now = dt.datetime.now(dt.timezone.utc)
    params = {
        "cityGAID": cfg["city_gaid"], "streetGAID": cfg["street_gaid"], "houseNo": cfg.get("house_no", HOUSE_NO),
        "fromDate": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "toDate": (now + dt.timedelta(days=LOOKAHEAD_DAYS)).strftime("%Y-%m-%dT23:59:59"),
        "getLightingSupport": "true", "getServicedSwitchingoff": "true",
    }
    raw = get(OUTAGES, params)
    if a.discover:
        print(json.dumps(raw, ensure_ascii=False, indent=1)[:6000])
    try:
        items = parse(raw)
    except ValueError as e:
        print("Surowa odpowiedź (początek):", json.dumps(raw, ensure_ascii=False)[:600])
        raise SystemExit(f"Błąd odpowiedzi Tauron: {e}")
    if not cached:
        save_config(cfg)   # zapamiętaj dopiero, gdy zapytanie się udało
    data = {"updated": now.isoformat(timespec="seconds"), "source": BASE + "/wylaczenia", "items": items}
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Zapisano {OUT}: {len(items)} wpisów")


if __name__ == "__main__":
    sys.exit(main())
