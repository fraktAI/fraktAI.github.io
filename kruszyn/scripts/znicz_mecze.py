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
DATE = re.compile(r"^(\d{1,2})\s+([^\W\d_]{3,})\.?(?:\s*/\s*(\d{1,2}))?$")
SLASH = re.compile(r"^/\s*(\d{1,2}|-)$")
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
        if m and norm(m.group(2))[:3] not in MONTHS:
            m = None
        j = i + 1                                       # indeks tokenu z godziną (po ewentualnym "/10")
        if m and j < len(tok) and SLASH.match(tok[j]):
            j += 1
        h = HEAD.match(t)
        if h and not TIME.match(t) and not m:
            close()
            comp = h.group(1).strip()
        elif m and j < len(tok) and (TIME.match(tok[j]) or tok[j] == "?:?"):
            close()
            mon = MONTHS.get(norm(m.group(2))[:3]) or int(m.group(3))
            yr = ys if mon >= 7 else ys + 1
            try:
                d = dt.date(yr, mon, int(m.group(1))).isoformat()
            except ValueError:
                d = None
            cur = {"data": d, "godz": tok[j] if tok[j] != "?:?" else None, "rozgrywki": comp,
                   "names": [], "nums": []}
            i = j
        elif t == "?:?" and cur is not None and cur["godz"] and len(cur["names"]) == 1 and cur["names"][-1] == tok[i - 1]:
            pass                                      # "?:?" w miejscu wyniku między drużynami (mecz jeszcze się nie odbył)
        elif t == "?:?":                              # mecz bez ustalonego terminu
            close()
            cur = {"data": None, "godz": None, "rozgrywki": comp, "names": [], "nums": []}
        elif cur is not None:
            if len(cur["names"]) >= 2:
                pass                                    # reszta wiersza (linki, stopka strony) – ignoruj
            elif NUMS.match(t) and re.search(r"\d", t):
                if len(cur["names"]) == 1:              # wynik leży między gospodarzem a gościem
                    cur["nums"] += [int(x) for x in re.findall(r"\d+", t)]
            elif norm(t) not in JUNK and len(t) >= 3 and re.search(r"[^\W\d_]", t):
                if not cur["names"] or cur["names"][-1] != t:
                    cur["names"].append(t)
        i += 1
    close()

    out = []
    for r in rows:
        names = r["names"]
        if len(names) < 2 or TEAM not in names[:2]:
            continue
        home, away = names[0], names[1]
        score = r["nums"][:2] if len(r["nums"]) >= 2 and max(r["nums"][:2]) <= 30 else None
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
        "ostatnie": played[:8], "najblizsze": dated[:6], "bez_terminu": len(undated),
    }


SAMPLE_M = """
<h4>Dolnośląskie | Klasa B</h4>
<ul>
<li><div><span>25 paź</span> <span>/10</span></div><div>11:00</div><div><img alt="Znicz Kruszyn"> Znicz Kruszyn</div><a href="/mecz/1"><span>5</span><span>2</span><span>:</span></a><div><a>LZS Łaziska</a></div></li>
<li><div><span>15 lis</span><span>/11</span></div><div>14:00</div><div>Znicz Kruszyn</div><a><span>3</span><span>2</span><span>:</span></a><div>LZS Brzeźnik</div><a>Zobacz relację</a></li>
<li><div>08 lis /11</div><div>13:30</div><div>Podgrodzie Raciborowice</div><a>1 4 :</a><div>Znicz Kruszyn</div></li>
<li><div>29 lis /11</div><div>11:00</div><div>Bóbr Dąbrowa Bolesławiecka</div><a>?:?</a><div>Znicz Kruszyn</div></li>
<li><span>-</span><span>-</span><span>-</span><span>/-</span><span>?:?</span><div>Znicz Kruszyn</div><span>-</span><span>-</span><span>:</span><div>Jawa Otok</div><span>Dodaj relację</span></li>
<li><div>-</div><span>/-</span><span>?:?</span><div>LZS Brzeźnik</div><span>-</span><span>:</span><div>Znicz Kruszyn</div><span>Dodaj relację</span></li>
<li><div>08 lis /11</div><div>13:30</div><div>Inny Klub</div><a>1 4 :</a><div>Trzeci Klub</div></li>
</ul>
<div>Stopka 50 50 ostatnia aktualizacja</div>
<h4>Polska | MECZE SPARINGOWE</h4>
<li><div>02 sie</div><div>/08</div><div>11:00</div><div>Znicz Kruszyn</div><a>7 5 :</a><div>KS Milików</div></li>
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
    assert len(ms) == 7, ms                       # mecz bez udziału Znicza odrzucony
    assert ms[0] == {"data": "2026-10-25", "godz": "11:00", "rozgrywki": "Klasa B", "gospodarz": "Znicz Kruszyn",
                     "gosc": "LZS Łaziska", "wynik": "5:2"}, ms[0]
    assert ms[1]["wynik"] == "3:2" and ms[1]["data"] == "2026-11-15", ms[1]
    assert ms[2]["wynik"] == "1:4" and ms[2]["gospodarz"] == "Podgrodzie Raciborowice" and ms[2]["gosc"] == TEAM, ms[2]
    assert ms[3]["data"] == "2026-11-29" and ms[3]["wynik"] is None
    assert ms[4]["data"] is None and ms[4]["wynik"] is None and ms[4]["gosc"] == "Jawa Otok", ms[4]
    assert ms[5]["data"] is None and ms[5]["wynik"] is None and ms[5]["gospodarz"] == "LZS Brzeźnik", ms[5]
    assert ms[6]["data"] == "2026-08-02" and ms[6]["rozgrywki"] == "MECZE SPARINGOWE" and ms[6]["wynik"] == "7:5", ms[6]
    tb = parse_table(tokens(SAMPLE_T))
    assert len(tb) == 3 and tb[2] == {"poz": 3, "druzyna": "Znicz Kruszyn", "pkt": 22, "m": 12, "w": 7, "r": 1, "p": 4,
                                      "bramki": "31:23"}, tb
    d = build(ms, tb, today)
    assert d["ostatnie"][0]["data"] == "2026-11-15" and d["ostatnie"][0]["rezultat"] == "W"
    assert d["najblizsze"][0]["data"] == "2026-11-29" and d["bez_terminu"] == 2 and d["pozycja"]["poz"] == 3
    print("selftest OK")


def diag(rm, rt, tm, tt):
    """Wydruk do logu: pokazuje, co robot widzi na stronach (do szukania przyczyn błędów)."""
    print(f"DIAGNOSTYKA: terminarz {len(rm)} znaków HTML, {len(tm)} tekstów; tabela {len(rt)} znaków, {len(tt)} tekstów")
    k = next((i for i, t in enumerate(tm) if "Terminarz" in t and "Znicz" in t), 0)
    print("DIAGNOSTYKA – teksty terminarza od nagłówka:", tm[k:k + 110])
    k = next((i for i, t in enumerate(tt) if t == "Pkt"), 0)
    print("DIAGNOSTYKA – teksty tabeli od 'Pkt':", tt[max(0, k - 4):k + 50])
    mo = re.search(r"\d{1,2}\s*(sty|lut|mar|kwi|maj|cze|lip|sie|wrz|pa\u017a|lis|gru)", rm, re.I)
    if mo:
        print("DIAGNOSTYKA – HTML wokół pierwszej daty:\n", rm[max(0, mo.start() - 400):mo.start() + 1600])
    else:
        print("DIAGNOSTYKA – w HTML terminarza NIE MA dat (dane ładowane skryptem?). Adresy skryptów/AJAX:")
        for u in sorted(set(re.findall(r"""(?:src|href|url)\s*[=:]\s*["']([^"']*(?:ajax|api|json|mecz|terminarz|kalendarz)[^"']*)["']""", rm, re.I)))[:25]:
            print("   ", u)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--discover", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    today = dt.datetime.now(TZ).date()
    rm, rt = fetch(URL_MATCHES), fetch(URL_TABLE)
    tm, tt = tokens(rm), tokens(rt)
    if a.discover:
        diag(rm, rt, tm, tt)
    matches, table = parse_matches(tm, today), parse_table(tt)
    played = [m for m in matches if m["wynik"]]

    if len(matches) < 3 or len(table) < 4 or not any(norm(r["druzyna"]) == norm(TEAM) for r in table):
        diag(rm, rt, tm, tt)
        raise SystemExit(f"Nie rozpoznano danych (meczów: {len(matches)}, wierszy tabeli: {len(table)}) "
                         "– zmienił się układ strony? Uruchom z --discover.")
    if not any(m["data"] and m["wynik"] for m in matches):
        diag(rm, rt, tm, tt)
        raise SystemExit("Nie rozpoznano żadnego rozegranego meczu z datą i wynikiem – zmienił się układ strony? "
                         "Uruchom z --discover.")
    data = build(matches, table, today)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    for m in data["ostatnie"][:3]:
        print("  ostatni:", m["data"], m["gospodarz"], m["wynik"], m["gosc"], f"[{m['rezultat']}]")
    print(f"Zapisano {OUT}: mecze {len(matches)} (rozegrane {len(played)}, bez terminu {data['bez_terminu']}), "
          f"tabela {len(table)} drużyn, pozycja Znicza: {data['pozycja'] and data['pozycja']['poz']}")


if __name__ == "__main__":
    sys.exit(main())
