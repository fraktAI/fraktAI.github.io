#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wysyła powiadomienia push (OneSignal) dla aplikacji Mój Kruszyn.

Tematy (tag w OneSignal): imgw, wydarzenia, znicz, prad, smieci.
Użycie (z folderu kruszyn):
  python3 scripts/powiadomienia.py             # normalny przebieg
  python3 scripts/powiadomienia.py --test      # jednorazowy test do osób z tagiem imgw=1
  python3 scripts/powiadomienia.py --selftest

Zmienne środowiskowe: ONESIGNAL_API_KEY (sekret GitHuba), PUSH_DRY_RUN=1 (tylko log, bez wysyłki).

Pamięć wysłanych: data/powiadomienia_stan.json. Dla tematów opartych na nowościach (imgw, wydarzenia,
wyniki Znicza, prąd) pierwszy przebieg tylko zapisuje to, co już jest, bez wysyłania.
Cisza nocna 22:00-7:00: powiadomienia czekają do rana; wyjątek: IMGW 3. stopnia i awarie prądu.
"""
import datetime as dt
import hashlib
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
STATE = Path("data/powiadomienia_stan.json")
TZ = ZoneInfo("Europe/Warsaw")
QUIET = (22, 7)
EVENING = 18             # od tej godziny dzień przed: zapowiedź meczu i przypomnienie o śmieciach
MIN_DEGREE, URGENT_DEGREE = 2, 3
MAX_PER_RUN = 8
KEEP_DAYS = 180          # wydarzenia bywają ogłaszane z dużym wyprzedzeniem
DNI = ["poniedziałek", "wtorek", "środa", "czwartek", "piątek", "sobota", "niedziela"]


def load(path, default):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def is_quiet(now):
    return now.hour >= QUIET[0] or now.hour < QUIET[1]


def cut(t, n):
    t = (t or "").strip()
    return t if len(t) <= n else t[:n - 1].rstrip() + "…"


def dm(d):                         # date -> "26.11"
    return f"{d.day:02d}.{d.month:02d}"


def hid(*parts):
    return hashlib.sha1("|".join(str(p) for p in parts).encode("utf-8")).hexdigest()[:10]


def cand(tag, keys, title, body, path, urgent=False, boot=None):
    return {"tag": tag, "keys": keys, "title": title, "body": body, "url": SITE + path, "urgent": urgent, "boot": boot}


# ---------- kandydaci wg tematów ----------
def c_imgw(now):
    out = []
    for i in load("ostrzezenia.json", {}).get("items", []):
        st = i.get("stopien") or 0
        if st < MIN_DEGREE:
            continue
        k = f"imgw:{i.get('id') or hid(i.get('zdarzenie'), i.get('od'))}:{st}"
        od, do = i.get("od"), i.get("do")
        f = lambda s: dt.datetime.strptime(s, "%Y-%m-%dT%H:%M").strftime("%d.%m %H:%M")
        body = f"Od {f(od)}" + (f" do {f(do)}" if do else "") + "." if od else ""
        if i.get("tresc"):
            body += " " + cut(i["tresc"], 140)
        out.append(cand("imgw", [k], f"⚠️ IMGW: {i.get('zdarzenie')} ({st}. stopień)", body.strip(), "#/pogoda", st >= URGENT_DEGREE, "imgw"))
    return out


def c_wydarzenia(now):
    ev = load("data/wydarzenia.json", {}).get("nadchodzace", [])
    if not ev:
        return []
    keys = [f"wyd:{hid(e['data'], e['nazwa'])}" for e in ev]
    def line(e):
        d = dt.date.fromisoformat(e["data"])
        return f"{DNI[d.weekday()]} {dm(d)}" + (f", {e['godz']}" if e.get("godz") else "") + (f" · {e['miejsce']}" if e.get("miejsce") else "")
    # jedno zbiorcze powiadomienie na przebieg: kandydat niesie wszystkie klucze, filtrowane później
    return [{"tag": "wydarzenia", "keys": keys, "events": ev, "line": line, "url": SITE + "#/wydarzenia", "urgent": False, "boot": "wydarzenia"}]


def c_znicz(now):
    z, out, today = load("znicz.json", {}), [], now.date()
    T = z.get("druzyna", "Znicz Kruszyn")
    for m in z.get("najblizsze", []):
        if not m.get("data"):
            continue
        d = dt.date.fromisoformat(m["data"]); k = (d - today).days
        if k == 1 and now.hour >= EVENING or k == 0:
            if k == 0 and m.get("godz") and m["godz"] <= now.strftime("%H:%M"):
                continue                                     # mecz już trwa lub się skończył
            body = f"{m['gospodarz']} – {m['gosc']}" + (f", godz. {m['godz']}" if m.get("godz") else "") + ("" if m["gospodarz"] == T else " (wyjazd)")
            out.append(cand("znicz", [f"znicz:zap:{m['data']}:{hid(m['gospodarz'], m['gosc'])}"],
                            "⚽ " + ("Jutro mecz Znicza" if k == 1 else "Dziś mecz Znicza"), body, "#/znicz"))
    for m in z.get("ostatnie", []):
        if m.get("wynik") and m["data"] >= (today - dt.timedelta(days=2)).isoformat():
            title = {"W": "⚽ Wygrana Znicza!", "P": "⚽ Porażka Znicza", "R": "⚽ Remis Znicza"}.get(m.get("rezultat"), "⚽ Wynik meczu Znicza")
            out.append(cand("znicz", [f"znicz:wynik:{m['data']}:{hid(m['gospodarz'], m['gosc'])}"], title,
                            f"{m['gospodarz']} {m['wynik']} {m['gosc']}", "#/znicz", boot="znicz_wynik"))
    return out


def c_prad(now):
    out, f = [], lambda s: dt.datetime.strptime(s, "%Y-%m-%dT%H:%M")
    for i in load("wylaczenia.json", {}).get("items", []):
        awaria = i.get("typ") == "awaria"
        if not awaria and i.get("do") and f(i["do"]) < now.replace(tzinfo=None):
            continue
        when = ""
        if i.get("od"):
            a = f(i["od"]); when = f"Od {dm(a)} {a:%H:%M}"
            if i.get("do"):
                b = f(i["do"]); when += f" do {b:%H:%M}" if b.date() == a.date() else f" do {dm(b)} {b:%H:%M}"
            when += ". "
        out.append(cand("prad", [f"prad:{i.get('typ')}:{i.get('od')}:{hid(i.get('tekst'))}"],
                        "⚡ Awaria prądu w Kruszynie" if awaria else "⚡ Planowane wyłączenie prądu",
                        when + cut(i.get("tekst"), 140), "#/prad", awaria, "prad"))
    return out


def c_smieci(now):
    if now.hour < EVENING:
        return []
    tm = (now.date() + dt.timedelta(days=1)).isoformat()
    labels = [fr["label"] for fr in load("data/waste.json", {}).get("fractions", []) if tm in fr.get("dates", [])]
    if not labels:
        return []
    return [cand("smieci", [f"smieci:{tm}"], "🗑️ Jutro odbiór odpadów", ", ".join(labels) + ". Wystaw pojemniki wieczorem.", "#/smieci")]


TOPICS = [c_imgw, c_wydarzenia, c_znicz, c_prad, c_smieci]


# ---------- wysyłka ----------
def push(tag, title, body, url, idem, api_key):
    payload = {"app_id": APP_ID, "target_channel": "push",
               "filters": [{"field": "tag", "key": tag, "relation": "=", "value": "1"}],
               "headings": {"en": title, "pl": title}, "contents": {"en": body, "pl": body},
               "url": url, "ttl": 43200, "idempotency_key": idem}
    req = urllib.request.Request(API, data=json.dumps(payload).encode("utf-8"), method="POST", headers={
        "Authorization": "Key " + api_key, "Content-Type": "application/json; charset=utf-8", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"OneSignal HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:300]}")


def run(now, state, sender, dry):
    """Zwraca (nowy_stan, liczba_wysłanych). state=None: brak pliku pamięci."""
    state = state or {}
    sent = dict(state.get("wyslane") or state.get("imgw_wyslane") or {})
    init = set(state.get("init") or (["imgw"] if "imgw_wyslane" in state else []))
    stamp = now.isoformat(timespec="minutes")
    cutoff = (now - dt.timedelta(days=KEEP_DAYS)).isoformat(timespec="minutes")
    sent = {k: v for k, v in sent.items() if v >= cutoff}
    cands = [c for fn in TOPICS for c in fn(now)]
    for g in {c["boot"] for c in cands if c["boot"]} - init:      # pierwszy przebieg tematu: tylko zapamiętaj
        n = 0
        for c in cands:
            if c["boot"] == g:
                for k in c["keys"]:
                    sent.setdefault(k, stamp); n += 1
        init.add(g); print(f"Temat „{g}” po raz pierwszy: zapisuję {n} istniejących pozycji bez wysyłania.")
    for g in ("imgw", "wydarzenia", "znicz_wynik", "prad"):
        init.add(g)
    quiet, count = is_quiet(now), 0
    for c in cands:
        new = [k for k in c["keys"] if k not in sent]
        if not new:
            continue
        if "events" in c:
            ev = [e for e, k in zip(c["events"], c["keys"]) if k in new]
            if len(ev) == 1:
                title, body = "📅 Nowe wydarzenie: " + cut(ev[0]["nazwa"], 60), c["line"](ev[0])
            else:
                title = f"📅 Nowe wydarzenia we wsi ({len(ev)})"
                body = cut("; ".join(f"{e['nazwa']} ({dm(dt.date.fromisoformat(e['data']))})" for e in ev), 160)
        else:
            title, body = c["title"], c["body"]
        if quiet and not c["urgent"]:
            print(f"Cisza nocna, odkładam do rana: {title}"); continue
        if count >= MAX_PER_RUN:
            print("Limit na przebieg, reszta w kolejnym."); break
        if dry:
            print(f"[PRÓBA] wysłałbym ({c['tag']}): {title} | {body}")
        else:
            res = sender(c["tag"], title, body, c["url"], str(uuid.uuid5(uuid.NAMESPACE_URL, "|".join(sorted(new)))))
            print(f"Wysłano ({c['tag']}): {title} -> {json.dumps(res, ensure_ascii=False)[:160]}")
            for k in new:
                sent[k] = stamp
        count += 1
    if not count and not any(not all(k in sent for k in c["keys"]) for c in cands):
        print("Brak nowych powiadomień.")
    return {"init": sorted(init), "wyslane": sent}, count


# ---------- test własny ----------
def selftest():
    import tempfile
    os.chdir(tempfile.mkdtemp()); Path("data").mkdir()
    W = lambda p, o: Path(p).write_text(json.dumps(o, ensure_ascii=False), encoding="utf-8")
    now = dt.datetime(2026, 11, 23, 12, 0, tzinfo=TZ)
    calls = []
    snd = lambda tag, t, b, u, i: calls.append((tag, t, b)) or {"id": "x"}
    ev1 = {"nazwa": "Mikołajki", "data": "2026-12-06", "godz": "17:30", "miejsce": "GOKiS"}
    W("ostrzezenia.json", {"items": [{"id": 1, "zdarzenie": "Wiatr", "stopien": 2, "od": "2026-11-23T12:00", "do": "2026-11-24T06:00"}]})
    W("data/wydarzenia.json", {"nadchodzace": [ev1]})
    W("wylaczenia.json", {"items": []})
    W("znicz.json", {"druzyna": "Znicz Kruszyn", "najblizsze": [], "ostatnie": [{"data": "2026-11-22", "gospodarz": "Znicz Kruszyn", "gosc": "A", "wynik": "1:0", "rezultat": "W"}]})
    W("data/waste.json", {"fractions": [{"label": "Plastik", "dates": ["2026-11-24"]}, {"label": "Szkło", "dates": ["2026-11-24"]}]})
    st, n = run(now, None, snd, False)
    assert n == 0 and calls == [], calls                                  # pierwszy przebieg: cisza, śmieci jeszcze za wcześnie
    ev2 = {"nazwa": "Jarmark", "data": "2026-12-13"}; ev3 = {"nazwa": "Bal", "data": "2026-12-20"}
    W("data/wydarzenia.json", {"nadchodzace": [ev1, ev2, ev3]})
    W("wylaczenia.json", {"items": [{"typ": "awaria", "od": "2026-11-23T11:00", "do": "2026-11-23T15:00", "tekst": "Kruszyn zwarcie"}]})
    W("znicz.json", {"druzyna": "Znicz Kruszyn", "najblizsze": [{"data": "2026-11-24", "godz": "11:00", "gospodarz": "X", "gosc": "Znicz Kruszyn"}],
                     "ostatnie": [{"data": "2026-11-22", "gospodarz": "Znicz Kruszyn", "gosc": "A", "wynik": "1:0", "rezultat": "W"},
                                  {"data": "2026-11-23", "gospodarz": "B", "gosc": "Znicz Kruszyn", "wynik": "0:2", "rezultat": "W"}]})
    ev = now.replace(hour=18)
    st, n = run(ev, st, snd, False)
    tags = sorted(c[0] for c in calls)
    assert tags == ["prad", "smieci", "wydarzenia", "znicz", "znicz"], calls        # 1 zbiorcze wydarzenia, zapowiedź + wynik
    assert any("(2)" in c[1] for c in calls if c[0] == "wydarzenia")
    k = len(calls); st, n = run(ev, st, snd, False); assert len(calls) == k and n == 0   # bez duplikatów
    W("wylaczenia.json", {"items": [{"typ": "planowane", "od": "2026-11-25T08:00", "do": "2026-11-25T14:00", "tekst": "Kruszyn plan"},
                                    {"typ": "awaria", "od": "2026-11-23T23:00", "tekst": "Kruszyn noc"}]})
    night = now.replace(hour=23); k = len(calls)
    st, n = run(night, st, snd, False)
    assert len(calls) == k + 1 and "Awaria" in calls[-1][1]                       # w nocy tylko awaria
    st, n = run(now.replace(day=24, hour=7), st, snd, False)
    assert "Planowane" in calls[-1][1]                                            # rano wysyła odłożone
    run(ev.replace(day=25), st, snd, True)
    print("selftest OK, wysłano powiadomień:", len(calls)); [print(" ", c) for c in calls]


def main():
    if "--selftest" in sys.argv:
        return selftest()
    dry, api_key = os.environ.get("PUSH_DRY_RUN") == "1", os.environ.get("ONESIGNAL_API_KEY", "")
    if "--test" in sys.argv:
        if not api_key:
            raise SystemExit("Brak ONESIGNAL_API_KEY (sekret GitHuba).")
        res = push("imgw", "🔔 Test powiadomień", "Jeśli to widzisz, powiadomienia z aplikacji Mój Kruszyn działają.", SITE, str(uuid.uuid4()), api_key)
        print("Wysłano test do osób z tagiem imgw=1:", json.dumps(res, ensure_ascii=False)[:300])
        if not res.get("id"):
            raise SystemExit("OneSignal nie przyjął powiadomienia (brak id, zapewne brak subskrybentów z tagiem imgw=1).")
        return
    if not api_key and not dry:
        raise SystemExit("Brak ONESIGNAL_API_KEY (sekret GitHuba).")
    now = dt.datetime.now(TZ)
    print(f"Tryb: {'PRÓBNY (nic nie wysyłam)' if dry else 'WYSYŁKA'}; {now:%Y-%m-%d %H:%M} czasu polskiego")
    new_state, n = run(now, load(STATE, None), lambda t, ti, b, u, i: push(t, ti, b, u, i, api_key), dry)
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(new_state, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Gotowe, powiadomień w tym przebiegu: {n}")


if __name__ == "__main__":
    sys.exit(main())
