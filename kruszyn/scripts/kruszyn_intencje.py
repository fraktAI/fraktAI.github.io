#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pobiera intencje mszalne z https://kruszyn.com/ogloszenia-parafialne/

Użycie (z folderu aplikacji):
  python3 scripts/kruszyn_intencje.py              # -> intencje.json
  python3 scripts/kruszyn_intencje.py --discover   # pokaż, co robot widzi na stronie (diagnostyka)
  python3 scripts/kruszyn_intencje.py --selftest

Format strony: nagłówek miesiąca ("Listopad roku Pańskiego 2026"), a pod nim wiersze
"2 poniedziałek 18:00 – treść intencji". Robot przechodzi tekst strony linia po linii,
zapamiętuje bieżący miesiąc i rok z nagłówka i buduje listę intencji.
Zabezpieczenia: dzień tygodnia musi zgadzać się z datą (inaczej wpis jest pomijany);
gdy nie rozpoznano żadnej intencji, plik NIE jest nadpisywany.
"""
import argparse
import datetime as dt
import html
import json
import re
import sys
import unicodedata
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from zoneinfo import ZoneInfo

URL = "https://kruszyn.com/ogloszenia-parafialne/"
OUT = Path("intencje.json")
TZ = ZoneInfo("Europe/Warsaw")
UA = {"User-Agent": "kruszyn-wies-app/1.0 (aplikacja mieszkancow wsi)"}

MONTHS = {"stycz": 1, "lut": 2, "mar": 3, "kwie": 4, "maj": 5, "czerw": 6,
          "lip": 7, "sierp": 8, "wrze": 9, "pazdz": 10, "listop": 11, "grud": 12}
DAYS = {"poniedzialek": 0, "wtorek": 1, "sroda": 2, "czwartek": 3, "piatek": 4, "sobota": 5, "niedziela": 6}

TIME = r"\d{1,2}[:.]\d{2}"
ENTRY = re.compile(rf"^\s*(\d{{1,2}})\s+([^\W\d_]+)\s+({TIME}(?:\s*(?:;|,|i|oraz)\s*{TIME})*)\s*(?:[–—:\-]+\s*)?(.*)$")
HEAD = re.compile(r"^\s*([^\W\d_]+)\s+(?:roku\s+pa[nń]skiego\s+)?(\d{4})\b", re.I)


def norm(s):
    s = s.replace("ł", "l").replace("Ł", "L")      # ł nie rozkłada się przy normalizacji Unicode
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


class Text(HTMLParser):
    BLOCK = {"br", "p", "div", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "section", "article", "hr", "table"}

    def __init__(self):
        super().__init__()
        self.out, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "nav", "noscript"):
            self.skip += 1
        if tag in self.BLOCK:
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "nav", "noscript") and self.skip:
            self.skip -= 1
        if tag in self.BLOCK:
            self.out.append("\n")

    def handle_data(self, d):
        if not self.skip:
            self.out.append(d)


def to_lines(raw_html):
    p = Text()
    p.feed(raw_html)
    text = html.unescape("".join(p.out)).replace("\xa0", " ").replace("​", "")
    text = re.sub(r"[*_`]+", "", text)           # ewentualny markdown
    return [re.sub(r"\s+", " ", l).strip() for l in text.split("\n") if l.strip()]


def month_of(word):
    w = norm(word)
    for k, v in MONTHS.items():
        if w.startswith(k):
            return v
    return None


def parse(lines):
    items, month, year, skipped = [], None, None, 0
    for line in lines:
        m = ENTRY.match(line)
        if m and month and year:
            day, dname, times, text = int(m.group(1)), norm(m.group(2)), m.group(3), m.group(4).strip()
            if dname not in DAYS:
                continue
            try:
                d = dt.date(year, month, day)
            except ValueError:
                skipped += 1
                continue
            if d.weekday() != DAYS[dname]:
                skipped += 1               # zły miesiąc/rok z nagłówka – nie zgadujemy
                continue
            for t in re.findall(TIME, times):
                h, mi = re.split(r"[:.]", t)
                items.append({"data": d.isoformat(), "godz": f"{int(h):02d}:{mi}", "tresc": text})
            continue
        h = HEAD.match(line)
        if h and month_of(h.group(1)) and not ENTRY.match(line):
            month, year = month_of(h.group(1)), int(h.group(2))
    items.sort(key=lambda x: (x["data"], x["godz"]))
    return items, skipped


def fetch():
    req = urllib.request.Request(URL, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


SAMPLE = """
<h3>Listopad roku Pańskiego 2026</h3>
<p><strong>2 poniedziałek 18:00</strong> – zbiorowa Msza za zmarłych<br>
<strong>3 wtorek 17:00</strong> – + Maria Grochała<br>
<strong>5 czwartek 17:00</strong> – o błogosławieństwo Boże dla kapłanów<br>
<strong>8 niedziela 8:00</strong> – + Irena<br><strong>8 niedziela 12:00</strong> – o błogosławieństwo Boże dla Róż Różańcowych<br>
<strong>9 wtorek 17:00</strong> – zły dzień tygodnia pominięty</p>
<h3>Grudzień roku Pańskiego 2026</h3>
<p><strong>1 wtorek 17:00; 18:00</strong> – + Jan</p>
"""


def selftest():
    items, skipped = parse(to_lines(SAMPLE))
    got = [(i["data"], i["godz"]) for i in items]
    assert ("2026-11-02", "18:00") in got and ("2026-11-08", "08:00") in got and ("2026-11-08", "12:00") in got, got
    assert ("2026-11-09", "17:00") not in got and skipped == 1, (got, skipped)
    print("selftest OK")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--discover", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    lines = to_lines(fetch())
    if a.discover:
        print("\n".join(lines[:80]))
    items, skipped = parse(lines)
    if not items:
        print("Pierwsze linie strony:\n" + "\n".join(lines[:40]))
        raise SystemExit("Nie rozpoznano żadnej intencji – zmienił się format strony?")
    today = dt.datetime.now(TZ).date()
    keep = [i for i in items if i["data"] >= (today - dt.timedelta(days=1)).isoformat()]
    OUT.write_text(json.dumps({"updated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                               "source": URL, "items": keep}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Zapisano {OUT}: {len(keep)} intencji (rozpoznano {len(items)}, pominięto {skipped} z błędnym dniem tygodnia)")


if __name__ == "__main__":
    sys.exit(main())
