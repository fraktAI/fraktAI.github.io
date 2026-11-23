#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wysyła powiadomienia push (OneSignal) o nowych ostrzeżeniach IMGW.

Użycie (z folderu kruszyn):
  python3 scripts/powiadomienia.py             # normalny przebieg
  python3 scripts/powiadomienia.py --test      # jednorazowy test do osób z tagiem imgw=1
  python3 scripts/powiadomienia.py --selftest

Zmienne środowiskowe:
  ONESIGNAL_API_KEY   klucz REST API (sekret GitHuba)
  PUSH_DRY_RUN=1      tryb próbny: tylko wypisuje, co by wysłał, nic nie wysyła i nie zapisuje jako wysłane

Pamięć wysłanych: data/powiadomienia_stan.json. Przy pierwszym uruchomieniu (brak pliku)
wszystkie aktualne ostrzeżenia są zapisywane jako już widziane, bez wysyłania.
Cisza nocna 22:00-7:00: ostrzeżenia 1.-2. stopnia czekają do rana (3. stopień idzie od razu).
"""
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from zoneinfo import ZoneInfo

APP_ID = "ff8708b2-789c-4754-9d47-405cb7f08145"
API = "https://api.onesignal.com/notifications?c=push"
SITE = "https://fraktai.github.io/kruszyn/"
IMGW = Path("ostrzezenia.json")
STATE = Path("data/powiadomienia_stan.json")
TZ = ZoneInfo("Europe/Warsaw")
QUIET = (22, 7)          # cisza nocna: od 22:00 do 7:00
MIN_DEGREE = 2           # stopień 1 pomijamy
URGENT_DEGREE = 3        # od tego stopnia powiadamiamy także w nocy
MAX_PER_RUN = 5
KEEP_DAYS = 30


def is_quiet(now):
    return now.hour >= QUIET[0] or now.hour < QUIET[1]


def key(it):
    base = it.get("id") or f"{it.get('zdarzenie')}|{it.get('od')}"
    return f"imgw:{base}:{it.get('stopien')}"       # wyższy stopień = nowe powiadomienie


def fmt(ts):
    if not ts:
        return ""
    d = dt.datetime.strptime(ts, "%Y-%m-%dT%H:%M")
    return d.strftime("%d.%m %H:%M")


def message(it):
    title = f"⚠️ IMGW: {it['zdarzenie']} ({it['stopien']}. stopień)"
    when = f"Od {fmt(it.get('od'))}" + (f" do {fmt(it.get('do'))}" if it.get("do") else "")
    body = when + "."
    t = (it.get("tresc") or "").strip()
    if t:
        body += " " + (t if len(t) <= 140 else t[:137].rstrip() + "…")
    return title, body


def send(it, api_key):
    """Wysyła do osób z tagiem imgw=1. Zwraca odpowiedź API; przy błędzie rzuca wyjątek."""
    title, body = message(it)
    return push(title, body, str(uuid.uuid5(uuid.NAMESPACE_URL, key(it))), api_key)


def push(title, body, idem, api_key):
    payload = {
        "app_id": APP_ID,
        "target_channel": "push",
        "filters": [{"field": "tag", "key": "imgw", "relation": "=", "value": "1"}],
        "headings": {"en": title, "pl": title},
        "contents": {"en": body, "pl": body},
        "url": SITE + "#/pogoda",
        "ttl": 43200,
        "idempotency_key": idem,
    }
    req = urllib.request.Request(API, data=json.dumps(payload).encode("utf-8"), method="POST", headers={
        "Authorization": "Key " + api_key, "Content-Type": "application/json; charset=utf-8", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"OneSignal HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:300]}")


def run(items, state, now, sender, dry):
    """Zwraca (nowy_stan, liczba_wysłanych). state=None oznacza pierwszy przebieg."""
    sent = dict((state or {}).get("imgw_wyslane", {}))
    cutoff = (now - dt.timedelta(days=KEEP_DAYS)).isoformat(timespec="minutes")
    sent = {k: v for k, v in sent.items() if v >= cutoff}
    stamp = now.isoformat(timespec="minutes")
    active = [i for i in items if (i.get("stopien") or 0) >= MIN_DEGREE]
    if state is None:
        for i in active:
            sent[key(i)] = stamp
        print(f"Pierwszy przebieg: zapisuję {len(active)} aktualnych ostrzeżeń jako widziane, bez wysyłania.")
        return {"imgw_wyslane": sent}, 0
    new = [i for i in active if key(i) not in sent]
    quiet = is_quiet(now)
    count = 0
    for i in new:
        if quiet and i["stopien"] < URGENT_DEGREE:
            print(f"Cisza nocna, odkładam do rana: {i['zdarzenie']} ({i['stopien']}. st.)")
            continue
        if count >= MAX_PER_RUN:
            print("Limit na przebieg, reszta w kolejnym.")
            break
        title, body = message(i)
        if dry:
            print(f"[PRÓBA] wysłałbym: {title} | {body}")
        else:
            res = sender(i)
            print(f"Wysłano: {title} -> {json.dumps(res, ensure_ascii=False)[:200]}")
            sent[key(i)] = stamp
        count += 1
    if not new:
        print("Brak nowych ostrzeżeń do wysłania.")
    return {"imgw_wyslane": sent}, count


def selftest():
    now = dt.datetime(2026, 11, 16, 10, 0, tzinfo=TZ)
    w = {"id": 1, "zdarzenie": "Silny wiatr", "stopien": 2, "od": "2026-11-16T12:00", "do": "2026-11-17T06:00", "tresc": "Wiatr."}
    m = {"id": 2, "zdarzenie": "Mróz", "stopien": 1, "od": "2026-11-16T12:00", "do": None}
    b = {"id": 3, "zdarzenie": "Burze", "stopien": 3, "od": "2026-11-16T12:00", "do": None}
    calls = []
    snd = lambda i: calls.append(i["id"]) or {"id": "x"}
    st, n = run([w, m], None, now, snd, False)               # pierwszy przebieg: nic nie wysyła
    assert n == 0 and calls == [] and key(w) in st["imgw_wyslane"]
    st, n = run([w, m, b], st, now, snd, False)               # tylko nowe, stopień 1 pominięty
    assert calls == [3] and n == 1
    st, n = run([w, m, b], st, now, snd, False)               # nic dwa razy
    assert calls == [3] and n == 0
    night = dt.datetime(2026, 11, 16, 23, 0, tzinfo=TZ)
    w2 = dict(w, id=4); b2 = dict(b, id=5)
    st, n = run([w2, b2], st, night, snd, False)              # noc: tylko 3. stopień
    assert calls == [3, 5] and key(w2) not in st["imgw_wyslane"]
    st, n = run([w2], st, dt.datetime(2026, 11, 17, 7, 0, tzinfo=TZ), snd, False)   # rano: odłożone
    assert calls == [3, 5, 4]
    st2, n = run([dict(w2, stopien=3)], st, now, snd, False)  # podniesiony stopień = nowe
    assert calls[-1] == 4 and n == 1
    st3, n = run([w, b], st, now, snd, True)                  # próba nic nie zapisuje
    print("selftest OK:", message(b))


def main():
    if "--selftest" in sys.argv:
        return selftest()
    if "--test" in sys.argv:        # jednorazowy test: nic nie zapisuje w pamięci wysłanych
        api_key = os.environ.get("ONESIGNAL_API_KEY", "")
        if not api_key:
            raise SystemExit("Brak ONESIGNAL_API_KEY (sekret GitHuba).")
        res = push("🔔 Test powiadomień", "Jeśli to widzisz, powiadomienia z aplikacji Mój Kruszyn działają.",
                   str(uuid.uuid4()), api_key)
        print("Wysłano test do osób z tagiem imgw=1:", json.dumps(res, ensure_ascii=False)[:300])
        if not res.get("id"):
            raise SystemExit("OneSignal nie przyjął powiadomienia (brak id, zapewne brak subskrybentów z tagiem imgw=1).")
        return
    dry = os.environ.get("PUSH_DRY_RUN") == "1"
    api_key = os.environ.get("ONESIGNAL_API_KEY", "")
    if not api_key and not dry:
        raise SystemExit("Brak ONESIGNAL_API_KEY (sekret GitHuba).")
    try:
        items = json.loads(IMGW.read_text(encoding="utf-8")).get("items", [])
    except (OSError, ValueError) as e:
        raise SystemExit(f"Nie mogę odczytać {IMGW}: {e}")
    try:
        state = json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        state = None
    now = dt.datetime.now(TZ)
    print(f"Tryb: {'PRÓBNY (nic nie wysyłam)' if dry else 'WYSYŁKA'}; {now:%Y-%m-%d %H:%M} czasu polskiego; ostrzeżeń: {len(items)}")
    new_state, n = run(items, state, now, lambda i: send(i, api_key), dry)
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(new_state, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Gotowe, powiadomień w tym przebiegu: {n}")


if __name__ == "__main__":
    sys.exit(main())
