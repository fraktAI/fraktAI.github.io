#!/usr/bin/env python3
"""Pobiera awarie i planowane wyłączenia prądu z publicznego API Tauron Dystrybucja
i zapisuje te, które dotyczą Kruszyna, do wylaczenia.json (czytane przez index.html).

Tylko biblioteka standardowa. Uruchamiane co godzinę przez GitHub Actions.
Zmienne środowiskowe (wszystkie opcjonalne):
  TAURON_TOWN          miejscowość do wyszukania            (domyślnie: Kruszyn)
  TAURON_AREA_HINT     fragment nazwy gminy/powiatu         (domyślnie: Bolesław)
  TAURON_MATCH         tekst, który musi być w komunikacie  (domyślnie: Kruszyn)
  TAURON_CITY_GAID     pomija wyszukiwanie miejscowości
  TAURON_STREET_GAIDS  lista GAID ulic po przecinku, pomija wyszukiwanie ulic
  TAURON_HOUSE_NO      numer domu do zapytania              (domyślnie: 1)
"""
import json, os, re, sys, urllib.parse, urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

BASE = "https://www.tauron-dystrybucja.pl"
TOWN = os.environ.get("TAURON_TOWN", "Kruszyn")
HINT = os.environ.get("TAURON_AREA_HINT", "Bolesław").lower()
MATCH = os.environ.get("TAURON_MATCH", "Kruszyn").lower()
HOUSE = os.environ.get("TAURON_HOUSE_NO", "1")
OUT = "wylaczenia.json"
TZ = ZoneInfo("Europe/Warsaw")
# ulice w Kruszynie, po których szukamy identyfikatora (wystarczy jedna trafiona)
STREET_NAMES = ["Klonowa", "Główna", "Świętojańska", "Lipowa", "Jodłowa"]


def log(*a):
    print(*a, flush=True)


def get(path, params=None):
    url = BASE + path + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(url, headers={
        "User-Agent": "kruszyn-village-page/1.0 (GitHub Actions, 1 zapytanie na godzinę)",
        "Accept": "application/json, text/plain, */*"})
    with urllib.request.urlopen(req, timeout=25) as r:
        raw = r.read().decode("utf-8", "replace")
    return json.loads(raw)  # Tauron bywa serwuje JSON jako text/plain


def as_list(x):
    if isinstance(x, list):
        return x
    if isinstance(x, dict):
        for v in x.values():
            if isinstance(v, list):
                return v
    return []


def gaid(o):
    for want in ("gaid", "id"):
        for k, v in o.items():
            if k.lower() == want and str(v).isdigit():
                return str(v)
    return None


def blob(o):
    return json.dumps(o, ensure_ascii=False).lower()


def find_city():
    if os.environ.get("TAURON_CITY_GAID"):
        return os.environ["TAURON_CITY_GAID"]
    for ep in ("/waapi/enum/geo/cities", "/iapi/city/GetCities"):
        try:
            data = as_list(get(ep, {"partName": TOWN}))
        except Exception as e:
            log(f"[miejscowość] {ep}: błąd {e}")
            continue
        log(f"[miejscowość] {ep}: {len(data)} wyników; przykład: {json.dumps(data[:2], ensure_ascii=False)[:400]}")
        cands = [o for o in data if isinstance(o, dict) and TOWN.lower() in blob(o)]
        pref = [o for o in cands if HINT in blob(o)]
        pick = pref or (cands if len(cands) == 1 else [])
        for o in pick:
            g = gaid(o)
            if g:
                log(f"[miejscowość] wybrano GAID {g}: {blob(o)[:200]}")
                return g
        log("[miejscowość] nie umiem wskazać jednoznacznie. Kandydaci:")
        for o in cands[:10]:
            log("   ", json.dumps(o, ensure_ascii=False)[:300])
    return None


def find_streets(city):
    if os.environ.get("TAURON_STREET_GAIDS"):
        return [s.strip() for s in os.environ["TAURON_STREET_GAIDS"].split(",") if s.strip()]
    found = []
    for name in STREET_NAMES:
        hit = False
        for ep, key in (("/waapi/enum/geo/streets", "ownerGAID"), ("/iapi/street/GetStreets", "ownerGaid")):
            try:
                data = as_list(get(ep, {key: city, "partName": name}))
            except Exception as e:
                log(f"[ulica {name}] {ep}: błąd {e}")
                continue
            for o in data:
                g = isinstance(o, dict) and gaid(o)
                if g and name.lower() in blob(o):
                    found.append(g)
                    log(f"[ulica {name}] GAID {g}")
                    hit = True
                    break
            if hit:
                break
        if len(found) >= 2:
            break
    return found


def parse_time(v):
    if v in (None, ""):
        return None
    s = str(v)
    m = re.match(r"/Date\((-?\d+)", s)
    try:
        if m:
            dt = datetime.fromtimestamp(int(m.group(1)) / 1000, tz=ZoneInfo("UTC"))
        else:
            dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=TZ)
    return dt.astimezone(TZ).strftime("%Y-%m-%dT%H:%M")


def pick_key(o, part):
    for k, v in o.items():
        if part in k.lower() and not isinstance(v, (dict, list)):
            return v
    return None


def query(city, street):
    now = datetime.now(TZ)
    d = get("/waapi/outages/address", {
        "cityGAID": city, "streetGAID": street, "houseNo": HOUSE,
        "fromDate": now.strftime("%Y-%m-%dT00:00:00"),
        "toDate": (now + timedelta(days=14)).strftime("%Y-%m-%dT23:59:59"),
        "getLightingSupport": "true", "getServicedSwitchingoff": "true"})
    items = d.get("OutageItems") if isinstance(d, dict) else None
    return items or []


def main():
    city = find_city()
    if not city:
        log("BŁĄD: nie znaleziono miejscowości. Ustaw zmienną TAURON_CITY_GAID (patrz log wyżej).")
        return 1
    streets = find_streets(city)
    if not streets:
        log("BŁĄD: nie znaleziono ulic. Ustaw zmienną TAURON_STREET_GAIDS.")
        return 1

    seen, ok = {}, False
    for st in streets:
        try:
            items = query(city, st)
        except Exception as e:
            log(f"[wyłączenia] ulica {st}: błąd {e}")
            continue
        ok = True
        log(f"[wyłączenia] ulica {st}: {len(items)} pozycji w okolicy")
        if items:
            log("   klucze:", sorted(items[0].keys()) if isinstance(items[0], dict) else type(items[0]))
        for o in items:
            if not isinstance(o, dict):
                continue
            msg = str(o.get("Message") or pick_key(o, "message") or pick_key(o, "descr") or "").strip()
            if MATCH not in msg.lower():
                continue
            oid = str(o.get("OutageId") or hash(msg))
            seen[oid] = {
                "id": oid,
                "typ": "planowane" if o.get("TypeId") == 1 else "awaria",
                "od": parse_time(pick_key(o, "start")),
                "do": parse_time(pick_key(o, "end")),
                "tekst": re.sub(r"\s+", " ", msg),
            }
    if not ok:
        log("BŁĄD: żadne zapytanie o wyłączenia się nie powiodło – zostawiam poprzedni plik.")
        return 1

    cutoff = (datetime.now(TZ) - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")
    items = [i for i in seen.values() if (i["do"] or i["od"] or "9") >= cutoff]
    items.sort(key=lambda i: (i["od"] or "", i["id"]))

    now = datetime.now(TZ)
    old = {}
    if os.path.exists(OUT):
        try:
            old = json.load(open(OUT, encoding="utf-8"))
        except Exception:
            pass
    fresh = False
    try:
        fresh = now - datetime.fromisoformat(old["updated"]) < timedelta(hours=12)
    except Exception:
        pass
    if old.get("items") == items and fresh:
        log("Bez zmian – nie nadpisuję pliku.")
        return 0
    json.dump({"updated": now.isoformat(timespec="minutes"), "source": "TAURON Dystrybucja",
               "items": items}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    log(f"Zapisano {len(items)} pozycji dla „{MATCH}”.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
