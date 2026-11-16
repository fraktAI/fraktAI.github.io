#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pobiera mecze i tabelę drużyny Znicz Kruszyn (klasa B, Jelenia Góra IV) z regiowyniki.pl

Użycie (z folderu aplikacji):
  python3 scripts/znicz_mecze.py              # -> znicz.json
  python3 scripts/znicz_mecze.py --discover   # pokaż, co robot widzi na stronach (diagnostyka)
  python3 scripts/znicz_mecze.py --selftest

Strony:
  terminarz: https://regiowyniki.pl/druzyna/Pilka_Nozna/Dolnoslaskie/Znicz_Kruszyn/
  tabela:    https://regiowyniki.pl/druzyna/Pilka_Nozna/Dolnoslaskie/Znicz_Kruszyn/tabela/

Robot nie opiera się na nazwach klas CSS (mogą się zmienić), tylko na samym tekście strony:
czyta po kolei teksty ze strony i rozpoznaje wzorce ("25 paź /10", "11:00", nazwy drużyn,
cyfry wyniku, nagłówki "Dolnośląskie | Klasa B"). Przy niezrozumiałej stronie kończy się
błędem i NIE nadpisuje poprzedniego pliku.
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

TEAM = "Znicz Kruszyn"
BASE = "https://regiowyniki.pl/druzyna/Pilka_Nozna/Dolnoslaskie/Znicz_Kruszyn/"
URL_MATCHES = BASE
URL_TABLE = BASE + "tabela/"
OUT = Path("znicz.json")
TZ = ZoneInfo("Europe/Warsaw")
UA = {"User-Agent": "kruszyn-wies-app/1.0 (aplikacja mieszkancow wsi)"}

MONTHS = {"sty": 1, "lut": 2, "mar": 3, "kwi": 4, "maj": 5, "cze": 6, "lip": 7, "sie": 8,
          "wrz": 9, "paz": 10, "lis": 11, "gru": 12}
JUNK = {"dodaj relacje", "zobacz relacje", "relacja na zywo", "l", "w", "r", "p", "forma", "-", ":"}


def norm(s):
    s = s.replace("ł", "l").replace("Ł", "L")
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower().strip()


class Tokens(HTMLParser):
    """Wszystkie niepuste teksty ze strony, po kolei (bez skryptów i stylów)."""

    def __init__(self):
        super().__init__()
        self.t, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg") and self.skip:
            self.skip -= 1

    def handle_data(self, d):
        if not self.skip:
            s = re.sub(r"\s+", " ", html.unescape(d).replace("\xa0", " ")).strip()
            if s:
                self.t.append(s)


def tokens(raw_html):
    p = Tokens()
    p.feed(raw_html)
    return p.t


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


# ---------------------------------------------------------------- terminarz
DATE = re.compile(r"^(\d{1,2})\s+([^\W\d_]{3,})\.?\s*/\s*(\d{1,2})$")
TIME = re.compile(r"^(\d{1,2}):(\d{2})$")
HEAD = re.compile(r"^[^|]{3,40}\|\s*(.+)$")          # "Dolnośląskie | Klasa B"
NUMS = re.compile(r"^[\d\s:]+$")


def season_start(today):
    return today.year if today.month >= 7 else today.year - 1


def parse_matches(tok, today):
    ys = season_start(today)
    comp, rows, cur = "", [], None

    def close():
        nonlocal cur
        if cur:
            rows.append(cur)
        cur = None

    i = 0
    while i < len(tok):
        t = tok[i]
        m = DATE.match(t)
        h = HEAD.match(t)
        if h and not TIME.match(t) and not m:
            close()
            comp = h.group(1).strip()
        elif m and i + 1 < len(tok) and (TIME.match(tok[i + 1]) or tok[i + 1] == "?:?"):
            close()
            mon = MONTHS.get(norm(m.group(2))[:3]) or int(m.group(3))
            yr = ys if mon >= 7 else ys + 1
            try:
                d = dt.date(yr, mon, int(m.group(1))).isoformat()
            except ValueError:
                d = None
            cur = {"data": d, "godz": tok[i + 1] if tok[i + 1] != "?:?" else None, "rozgrywki": comp,
                   "names": [], "nums": []}
            i += 1
        elif t == "?:?" and cur is not None and cur["godz"] and len(cur["names"]) == 1 and cur["names"][-1] == tok[i - 1]:
            pass                                      # "?:?" w miejscu wyniku między drużynami (mecz jeszcze się nie odbył)
        elif t == "?:?":                              # mecz bez ustalonego terminu
            close()
            cur = {"data": None, "godz": None, "rozgrywki": comp, "names": [], "nums": []}
        elif cur is not None:
            if NUMS.match(t) and re.search(r"\d", t):
                cur["nums"] += [int(x) for x in re.findall(r"\d+", t)]
            elif norm(t) not in JUNK and len(t) >= 3 and re.search(r"[^\W\d_]", t):
                cur["names"].append(t)
        i += 1
    close()

    out = []
    for r in rows:
        names = []
        for n in r["names"]:                          # zdublowane nazwy (alt/tekst) zostają raz pod rząd
            if not names or names[-1] != n:
                names.append(n)
        if len(names) < 2 or TEAM not in names[:2]:
            continue
        home, away = names[0], names[1]
        score = r["nums"][:2] if len(r["nums"]) >= 2 else None
        out.append({"data": r["data"], "godz": r["godz"], "rozgrywki": r["rozgrywki"],
                    "gospodarz": home, "gosc": away,
                    "wynik": f"{score[0]}:{score[1]}" if score else None})
    return out


# ------------------------------------------------------------------- tabela
def parse_table(tok):
    """Pierwsza tabela (zestawienie ogólne): miejsce, drużyna, Pkt, M, W, R, P, bramki."""
    cols = None
    if "Pkt" in tok:
        a = tok.index("Pkt")
        cols = [norm(x) for x in tok[a:a + 6] if norm(x) in ("pkt", "m", "w", "r", "p", "bramki")]
    cols = cols if cols and len(cols) >= 4 else ["pkt", "m", "w", "r", "p", "bramki"]
    rows, expect, i = [], 1, 0
    while i < len(tok) - 2:
        if tok[i] == str(expect) and re.search(r"[^\W\d_]{2,}", tok[i + 1]) and not NUMS.match(tok[i + 1]):
            name, vals, j = tok[i + 1], [], i + 2
            while j < len(tok) and len(vals) < len(cols):
                if re.fullmatch(r"\d+(:\d+)?", tok[j]):
                    vals.append(tok[j])
                    j += 1
                elif norm(tok[j]) in ("w", "r", "p"):  # litery formy – koniec liczb
                    break
                else:
                    break
            if len(vals) == len(cols):
                row = {"poz": expect, "druzyna": name}
                for c, v in zip(cols, vals):
                    row[c] = v if c == "bramki" else int(v)
                rows.append(row)
                expect += 1
                i = j
                continue
        i += 1
    return rows


# ------------------------------------------------------------------- budowa
def build(matches, table, today):
    now_s = today.isoformat()
    played = [m for m in matches if m["wynik"]]
    played.sort(key=lambda m: (m["data"] or "", m["godz"] or ""), reverse=True)
    up = [m for m in matches if not m["wynik"]]
    dated = sorted([m for m in up if m["data"] and m["data"] >= now_s], key=lambda m: (m["data"], m["godz"] or ""))
    undated = [m for m in up if not m["data"]]
    me = next((r for r in table if norm(r["druzyna"]) == norm(TEAM)), None)

    def res(m):
        h, a = [int(x) for x in m["wynik"].split(":")]
        mine = h if m["gospodarz"] == TEAM else a
        opp = a if m["gospodarz"] == TEAM else h
        return "W" if mine > opp else "P" if mine < opp else "R"

    for m in played:
        m["rezultat"] = res(m)
    return {
        "updated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "source": URL_MATCHES, "source_table": URL_TABLE, "druzyna": TEAM,
        "liga": "Klasa B, Jelenia Góra IV", "sezon": f"{season_start(today)}/{str(season_start(today) + 1)[2:]}",
        "tabela": table, "pozycja": me,
        "ostatnie": played[:6], "najblizsze": dated[:6], "bez_terminu": len(undated),
    }


SAMPLE_M = """
<h4>Dolnośląskie | Klasa B</h4>
<ul>
<li><span>25 paź /10</span><span>11:00</span><img alt="Znicz Kruszyn"><span>Znicz Kruszyn</span><a href="/mecz/1">5 2 :</a><a>LZS Łaziska</a></li>
<li><span>15 lis /11</span><span>14:00</span><span>Znicz Kruszyn</span><a>3 2 :</a><span>LZS Brzeźnik</span><a>Zobacz relację</a></li>
<li><span>29 lis /11</span><span>11:00</span><span>Bóbr Dąbrowa Bolesławiecka</span><a>?:?</a><span>Znicz Kruszyn</span></li>
<li><span>-</span><span>-</span><span>/-</span><span>?:?</span><span>Znicz Kruszyn</span><span>-</span><span>:</span><span>Jawa Otok</span><span>Dodaj relację</span></li>
<li><span>08 lis /11</span><span>13:30</span><span>Inny Klub</span><a>1 4 :</a><span>Trzeci Klub</span></li>
</ul>
<h4>Polska | MECZE SPARINGOWE</h4>
<li><span>02 sie /08</span><span>11:00</span><span>Znicz Kruszyn</span><a>7 5 :</a><span>KS Milików</span></li>
"""
SAMPLE_T = """
<table><tr><th>Miejsce</th><th>Drużyna</th><th>Pkt</th><th>M</th><th>W</th><th>R</th><th>P</th><th>Bramki</th><th>Forma</th></tr>
<tr><td>1</td><td>Bóbr Dąbrowa Bolesławiecka</td><td>29</td><td>12</td><td>9</td><td>2</td><td>1</td><td>50:17</td><td>W P R W R</td></tr>
<tr><td>2</td><td>Leśnik Osiecznica</td><td>28</td><td>12</td><td>9</td><td>1</td><td>2</td><td>44:18</td><td>W W W</td></tr>
<tr><td>3</td><td>Znicz Kruszyn</td><td>22</td><td>12</td><td>7</td><td>1</td><td>4</td><td>31:23</td><td>W W P P W</td></tr></table>
"""


def selftest():
    today = dt.date(2026, 11, 16)
    ms = parse_matches(tokens(SAMPLE_M), today)
    assert len(ms) == 5, ms                       # mecz bez udziału Znicza odrzucony
    assert ms[0] == {"data": "2026-10-25", "godz": "11:00", "rozgrywki": "Klasa B", "gospodarz": "Znicz Kruszyn",
                     "gosc": "LZS Łaziska", "wynik": "5:2"}, ms[0]
    assert ms[3]["data"] is None and ms[3]["wynik"] is None and ms[3]["gosc"] == "Jawa Otok", ms[3]
    assert ms[2]["data"] == "2026-11-29" and ms[2]["wynik"] is None
    assert ms[4]["data"] == "2026-08-02" and ms[4]["rozgrywki"] == "MECZE SPARINGOWE"
    tb = parse_table(tokens(SAMPLE_T))
    assert len(tb) == 3 and tb[2] == {"poz": 3, "druzyna": "Znicz Kruszyn", "pkt": 22, "m": 12, "w": 7, "r": 1, "p": 4,
                                      "bramki": "31:23"}, tb
    d = build(ms, tb, today)
    assert d["ostatnie"][0]["data"] == "2026-11-15" and d["ostatnie"][0]["rezultat"] == "W"
    assert d["najblizsze"][0]["data"] == "2026-11-29" and d["bez_terminu"] == 1 and d["pozycja"]["poz"] == 3
    print("selftest OK")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--discover", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    today = dt.datetime.now(TZ).date()
    tm, tt = tokens(fetch(URL_MATCHES)), tokens(fetch(URL_TABLE))
    if a.discover:
        print("TERMINARZ (pierwsze 120 tekstów):", tm[:120], "\nTABELA (pierwsze 120):", tt[:120], sep="\n")
    matches, table = parse_matches(tm, today), parse_table(tt)
    played = [m for m in matches if m["wynik"]]
    if len(matches) < 3 or len(table) < 4 or not any(norm(r["druzyna"]) == norm(TEAM) for r in table):
        raise SystemExit(f"Nie rozpoznano danych (meczów: {len(matches)}, wierszy tabeli: {len(table)}) "
                         "– zmienił się układ strony? Uruchom z --discover.")
    data = build(matches, table, today)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Zapisano {OUT}: mecze {len(matches)} (rozegrane {len(played)}, bez terminu {data['bez_terminu']}), "
          f"tabela {len(table)} drużyn, pozycja Znicza: {data['pozycja'] and data['pozycja']['poz']}")


if __name__ == "__main__":
    sys.exit(main())
