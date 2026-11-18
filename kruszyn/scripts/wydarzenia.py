#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pobiera wydarzenia z zakładki „Publiczne” arkusza Google (odpowiedzi z formularza).

Użycie (z folderu aplikacji):
  python3 scripts/wydarzenia.py              # -> data/wydarzenia.json + data/kruszyn-wydarzenia.ics
  python3 scripts/wydarzenia.py --selftest

Adres opublikowanej zakładki (CSV) jest w pliku wydarzenia_url.txt (jedna linia) albo w zmiennej
środowiskowej WYDARZENIA_CSV_URL. Gdy go nie ma, skrypt nic nie robi (kończy się bez błędu).

Zakładka „Publiczne” zawiera tylko zatwierdzone wpisy i tylko kolumny przeznaczone do pokazania:
Nazwa wydarzenia, Data, Kategoria, Godzina, Data zakończenia, Miejsce, Opis, Organizator, Telefon, Link.
Robot i tak sprawdza każdy wiersz: wpis z błędną datą lub bez nazwy jest pomijany.
Przy błędzie pobierania poprzedni plik NIE jest nadpisywany.
"""
import csv
import datetime as dt
import hashlib
import io
import json
import os
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

URL_FILE = Path("wydarzenia_url.txt")
OUT = Path("data/wydarzenia.json")
ICS = Path("data/kruszyn-wydarzenia.ics")
TZ = ZoneInfo("Europe/Warsaw")
UA = {"User-Agent": "kruszyn-wies-app/1.0 (aplikacja mieszkancow wsi)"}
PAST_KEEP = 5
CATEGORIES = ["Kościół i parafia", "Sport", "Kultura i zabawa", "Spotkanie lub zebranie",
              "Urząd i sprawy gminy", "Dla dzieci", "Inne"]
FIELDS = {"nazwa wydarzenia": "nazwa", "data": "data", "kategoria": "kategoria", "godzina": "godz",
          "data zakonczenia": "data_do", "miejsce": "miejsce", "opis": "opis",
          "organizator": "organizator", "telefon": "telefon", "link": "link"}
MAXLEN = {"nazwa": 80, "miejsce": 100, "opis": 400, "organizator": 80}


def norm(s):
    s = str(s).replace("ł", "l").replace("Ł", "L")
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower().strip()


def clean(s, limit=None):
    s = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", "", str(s or "")).strip()
    s = re.sub(r"[ \t]+", " ", s)
    return s[:limit] if limit else s


def parse_date(s):
    s = clean(s)
    if not s:
        return None
    s = s.split(" ")[0]
    if re.fullmatch(r"\d{5}(?:[.,]\d+)?", s):      # numer seryjny arkusza (QUERY gubi format daty)
        return (dt.date(1899, 12, 30) + dt.timedelta(days=int(re.split(r"[.,]", s)[0]))).isoformat()
    m = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", s)
    if m:
        y, mo, d = map(int, m.groups())
    else:
        m = re.fullmatch(r"(\d{1,2})[./-](\d{1,2})[./-](\d{4})", s)     # dd.mm.rrrr (polski zapis)
        if not m:
            return None
        d, mo, y = map(int, m.groups())
    try:
        return dt.date(y, mo, d).isoformat()
    except ValueError:
        return None


def parse_time(s):
    s = clean(s)
    if not s:
        return None
    if re.fullmatch(r"0?[.,]\d+|[01]", s):         # ułamek doby, np. 0,7083 = 17:00
        mins = round(float(s.replace(",", ".")) * 1440) % 1440
        return f"{mins // 60:02d}:{mins % 60:02d}"
    m = re.fullmatch(r"(\d{1,2})[:.](\d{2})(?::\d{2})?\s*([AaPp][Mm])?", s)
    if not m:
        return None
    h, mi, ap = int(m.group(1)), int(m.group(2)), m.group(3)
    if ap:
        h = h % 12 + (12 if ap.lower() == "pm" else 0)
    return f"{h:02d}:{mi:02d}" if h < 24 and mi < 60 else None


def parse_rows(text):
    """CSV z zakładki Publiczne -> lista poprawnych wydarzeń. Zwraca (lista, liczba_pominiętych)."""
    rows = list(csv.reader(io.StringIO(text.lstrip("\ufeff"))))
    if not rows:
        return None, 0
    head = [norm(h) for h in rows[0]]
    if "nazwa wydarzenia" not in head or "data" not in head:
        raise ValueError("w pliku brak nagłówków 'Nazwa wydarzenia' i 'Data' (to nie jest zakładka Publiczne?)")
    idx = {FIELDS[h]: i for i, h in enumerate(head) if h in FIELDS}
    items, skipped = [], 0
    for r in rows[1:]:
        if not any(c.strip() for c in r):
            continue
        g = lambda k: r[idx[k]] if k in idx and idx[k] < len(r) else ""
        name, date = clean(g("nazwa"), MAXLEN["nazwa"]), parse_date(g("data"))
        if not name or not date:
            skipped += 1
            continue
        end = parse_date(g("data_do"))
        if end and end <= date:
            end = None
        cat = clean(g("kategoria"))
        phone = re.sub(r"[^0-9+ \-]", "", clean(g("telefon")))
        link = clean(g("link"))
        items.append({
            "nazwa": name, "kategoria": cat if cat in CATEGORIES else "Inne",
            "data": date, "godz": parse_time(g("godz")), "data_do": end,
            "miejsce": clean(g("miejsce"), MAXLEN["miejsce"]), "opis": clean(g("opis"), MAXLEN["opis"]),
            "organizator": clean(g("organizator"), MAXLEN["organizator"]),
            "telefon": phone if len(re.sub(r"\D", "", phone)) >= 9 else "",
            "link": link if re.match(r"https?://", link, re.I) else "",
        })
    return items, skipped


def split(items, today):
    ts = today.isoformat()
    last = lambda e: e["data_do"] or e["data"]
    upcoming = sorted([e for e in items if last(e) >= ts], key=lambda e: (e["data"], e["godz"] or ""))
    past = sorted([e for e in items if last(e) < ts], key=lambda e: (e["data"], e["godz"] or ""), reverse=True)[:PAST_KEEP]
    return upcoming, past


def esc(t):
    return t.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def fold(line):
    parts, b, limit = [], line.encode("utf-8"), 75
    while len(b) > limit:
        cut = limit
        while (b[cut] & 0xC0) == 0x80:
            cut -= 1
        parts.append(b[:cut].decode("utf-8"))
        b, limit = b[cut:], 74
    parts.append(b.decode("utf-8"))
    return "\r\n ".join(parts)


def make_ics(events):
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Kruszyn//Wydarzenia//PL", "CALSCALE:GREGORIAN",
             "METHOD:PUBLISH", "X-WR-CALNAME:Wydarzenia – Kruszyn", "X-WR-TIMEZONE:Europe/Warsaw",
             "REFRESH-INTERVAL;VALUE=DURATION:PT6H", "X-PUBLISHED-TTL:PT6H"]
    for e in events:
        uid = hashlib.sha1(f"{e['data']}|{e['godz']}|{e['nazwa']}".encode("utf-8")).hexdigest()[:16]
        d0 = dt.date.fromisoformat(e["data"])
        desc = " ".join(x for x in (e["opis"], f"Organizator: {e['organizator']}." if e["organizator"] else "",
                                    f"Tel. {e['telefon']}." if e["telefon"] else "", e["link"]) if x)
        lines += ["BEGIN:VEVENT", f"UID:{uid}@kruszyn", "DTSTAMP:20260101T000000Z"]
        if e["godz"]:
            h, m = map(int, e["godz"].split(":"))
            start = dt.datetime.combine(d0, dt.time(h, m))
            lines += [f"DTSTART;TZID=Europe/Warsaw:{start:%Y%m%dT%H%M%S}",
                      f"DTEND;TZID=Europe/Warsaw:{start + dt.timedelta(hours=2):%Y%m%dT%H%M%S}"]
            trig = "-PT2H"
        else:
            d1 = dt.date.fromisoformat(e["data_do"]) if e["data_do"] else d0
            lines += [f"DTSTART;VALUE=DATE:{d0:%Y%m%d}", f"DTEND;VALUE=DATE:{d1 + dt.timedelta(days=1):%Y%m%d}"]
            trig = "-PT6H"
        lines += [f"SUMMARY:{esc(e['nazwa'])}"]
        if e["miejsce"]:
            lines.append(f"LOCATION:{esc(e['miejsce'])}")
        if desc:
            lines.append(f"DESCRIPTION:{esc(desc)}")
        lines += ["BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{esc('Wydarzenie: ' + e['nazwa'])}", f"TRIGGER:{trig}",
                  "END:VALARM", "END:VEVENT"]
    lines.append("END:VCALENDAR")
    tz = ["BEGIN:VTIMEZONE", "TZID:Europe/Warsaw", "BEGIN:STANDARD", "DTSTART:19701025T030000", "TZOFFSETFROM:+0200",
          "TZOFFSETTO:+0100", "RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU", "END:STANDARD", "BEGIN:DAYLIGHT",
          "DTSTART:19700329T020000", "TZOFFSETFROM:+0100", "TZOFFSETTO:+0200", "RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU",
          "END:DAYLIGHT", "END:VTIMEZONE"]
    i = next(k for k, l in enumerate(lines) if l.startswith("BEGIN:VEVENT")) if events else len(lines) - 1
    lines = lines[:i] + tz + lines[i:]
    return ("\r\n".join(fold(l) for l in lines) + "\r\n").encode("utf-8")


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def selftest():
    csv_text = (
        "Nazwa wydarzenia ,Data,Kategoria,Godzina,Data zakończenia,Miejsce,Opis,Organizator,Telefon,Link\n"
        "Zebranie wiejskie,2026-11-21,Spotkanie lub zebranie,18:00,,Świetlica,\"Omówimy plan, budżet\",Sołtys,600 123 456,https://example.pl\n"
        "Dożynki,29.08.2026,Kultura i zabawa,,30.08.2026,Boisko,,OSP,12,javascript:alert(1)\n"
        "Turniej,2026-12-05,Sport,10:30:00,,Hala,,,,\n"
        "Bez daty,,Sport,,,,,,,\n"
        ",2026-12-01,Sport,,,,,,,\n"
        "Zła kategoria,2026-11-10,Nieznana,6:00 PM,,,,,,\n")
    items, skipped = parse_rows(csv_text)
    assert len(items) == 4 and skipped == 2, (len(items), skipped)
    assert items[0]["godz"] == "18:00" and items[0]["opis"] == "Omówimy plan, budżet" and items[0]["link"] == "https://example.pl"
    assert items[1]["data"] == "2026-08-29" and items[1]["data_do"] == "2026-08-30" and items[1]["link"] == "" and items[1]["telefon"] == ""
    assert items[2]["godz"] == "10:30" and items[3]["kategoria"] == "Inne" and items[3]["godz"] == "18:00"
    up, past = split(items, dt.date(2026, 11, 18))
    assert [e["nazwa"] for e in up] == ["Zebranie wiejskie", "Turniej"], up
    assert [e["nazwa"] for e in past] == ["Zła kategoria", "Dożynki"], past
    ics = make_ics(up + past).decode("utf-8")
    assert ics.count("BEGIN:VEVENT") == 4 and "\r\n" in ics and "DTSTART;TZID=Europe/Warsaw:20261121T180000" in ics
    assert all(len(l.encode("utf-8")) <= 75 for l in ics.split("\r\n"))
    try:
        parse_rows("<html>Zaloguj się</html>")
        raise AssertionError("powinien być błąd")
    except ValueError:
        pass
    print("selftest OK")


def main():
    if "--selftest" in sys.argv:
        return selftest()
    url = os.environ.get("WYDARZENIA_CSV_URL") or (URL_FILE.read_text(encoding="utf-8").strip() if URL_FILE.exists() else "")
    if not url or url.startswith("#"):
        print("Brak adresu arkusza (wydarzenia_url.txt) – pomijam wydarzenia.")
        return
    try:
        items, skipped = parse_rows(fetch(url))
    except ValueError as e:
        raise SystemExit(f"Błąd danych z arkusza: {e}")
    old = None
    if OUT.exists():
        try:
            old = json.loads(OUT.read_text(encoding="utf-8"))
        except ValueError:
            pass
    if items is None:      # pusta odpowiedź: nie kasuj dotychczasowych wydarzeń przez chwilową usterkę
        if old and (old.get("nadchodzace") or old.get("minione")):
            raise SystemExit("Arkusz zwrócił pusty plik, a wcześniej były wydarzenia – zostawiam stare dane.")
        items = []
    today = dt.datetime.now(TZ).date()
    up, past = split(items, today)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({"updated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                               "nadchodzace": up, "minione": past}, ensure_ascii=False, indent=1), encoding="utf-8")
    ICS.write_bytes(make_ics(up + past))
    print(f"Zapisano {OUT}: nadchodzące {len(up)}, minione {len(past)}, pominięto błędnych wierszy: {skipped}")


if __name__ == "__main__":
    sys.exit(main())
