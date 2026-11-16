#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pobiera harmonogram wywozu odpadów dla Kruszyna (gm. Bolesławiec) z com-d.pl.

Użycie:
  python3 scripts/kruszyn_scraper.py --out data/waste.json --embed index.html   # pobranie ze strony
  python3 scripts/kruszyn_scraper.py --seed --out data/waste.json --embed index.html   # dane startowe (bez sieci)
  python3 scripts/kruszyn_scraper.py --selftest                            # test parsera

Strona podaje dla każdej frakcji: częstotliwość, najbliższy odbiór, kolejne terminy
i wyjątki (święta). Pełny rok skrypt odtwarza z reguły (np. co 4 tygodnie, tygodnie
nieparzyste) i dokłada wyjątki. Bez zewnętrznych bibliotek.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
import urllib.request
from pathlib import Path

URL = "http://www.com-d.pl/komunalne/harm/boleslawiec-{year}r-gmina/kruszyn/{page}"
PAGES = [
    "tnp-odpady-zmieszane",
    "tp-odpady-biodegradowalne",
    "inne-odpady-plastik",
    "inne-odpady-szklo",
    "inne-odpady-makulatura",
    "inne-odpady-zbiorki",
]
PHONE = "76 870 21 68"  # Biuro Obsługi Klienta COM-D, "pozostałe gminy"
LABELS = {
    "zmieszane": "Odpady zmieszane",
    "bio": "Bioodpady",
    "plastik": "Plastik",
    "szklo": "Szkło",
    "makulatura": "Makulatura",
    "odziez": "Odzież i tekstylia",
    "gabaryty": "Gabaryty, RTV, opony",
}
ORDER = list(LABELS)

DATE_RE = re.compile(r"(\d{1,2})\.(\d{1,2})\.(\d{4})")
EXC_RE = re.compile(r"(\d{1,2}\.\d{1,2}\.\d{4})\s*←[^0-9]*(\d{1,2}\.\d{1,2}\.\d{4})")


def to_date(s: str) -> dt.date:
    d, m, y = map(int, DATE_RE.fullmatch(s.strip()).groups())
    return dt.date(y, m, d)


# ---------- parsowanie ----------
def html_to_text(raw: str) -> str:
    raw = re.sub(r"(?is)<(script|style).*?</\1>", " ", raw)
    raw = re.sub(r"(?i)<br\s*/?>|</(p|div|li|tr|h\d)>", "\n", raw)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    raw = html.unescape(raw)
    raw = re.sub(r"[ \t\xa0]+", " ", raw)
    return re.sub(r"\n\s*\n+", "\n", raw)


def section(block: str, start: str, stops: list[str]) -> str:
    i = block.find(start)
    if i < 0:
        return ""
    j = len(block)
    for s in stops:
        k = block.find(s, i + len(start))
        if k != -1:
            j = min(j, k)
    return block[i:j]


def parse_rule(freq: str):
    f = freq.lower()
    if "nieparzyst" in f:
        return {"type": "parity", "parity": 1}
    if "parzyst" in f:
        return {"type": "parity", "parity": 0}
    m = re.search(r"co\s+(\d+)\s+tygod", f)
    if m:
        return {"type": "every", "weeks": int(m.group(1))}
    if "dwa tygodnie" in f:
        return {"type": "every", "weeks": 2}
    if re.search(r"co\s+tydzie", f):
        return {"type": "every", "weeks": 1}
    return None  # np. "2x w roku" - tylko daty podane wprost


def fraction_id(page: str, freq: str) -> str:
    f = freq.lower()
    if page.endswith("zmieszane"):
        return "zmieszane"
    if page.endswith("biodegradowalne"):
        return "bio"
    if page.endswith("plastik"):
        return "plastik"
    if page.endswith("szklo"):
        return "szklo"
    if page.endswith("makulatura"):
        return "makulatura"
    return "odziez" if ("odzie" in f or "tekstyl" in f) else "gabaryty"


def expand(rule, anchor, listed, exceptions):
    """Odtwarza daty do końca roku z reguły + dokłada wyjątki (święta)."""
    dates = set(listed)
    if anchor:
        dates.add(anchor)
    if anchor and rule:
        base = next((orig for new, orig in exceptions if new == anchor), anchor)
        end = dt.date(base.year, 12, 31)
        d = base
        if rule["type"] == "parity":
            while d <= end:
                if d.isocalendar()[1] % 2 == rule["parity"]:
                    dates.add(d)
                d += dt.timedelta(days=7)
        else:
            while d <= end:
                dates.add(d)
                d += dt.timedelta(days=7 * rule["weeks"])
    for new, orig in exceptions:
        if orig in dates:
            dates.discard(orig)
            dates.add(new)
    return sorted(dates)


def parse_page(page: str, text: str):
    out = []
    for block in re.split(r"Harmonogram dotyczy:", text)[1:]:
        m = re.search(r"Częstotliwość obiorów:\s*(.+)", block)
        if not m:
            continue
        freq = m.group(1).strip()
        nxt = DATE_RE.search(section(block, "Najbliższy odbiór",
                                     ["Kolejne terminy", "Wyjątki", "Kalendarz"]))
        anchor = to_date(nxt.group(0)) if nxt else None
        listed = [to_date(x.group(0)) for x in DATE_RE.finditer(
            section(block, "Kolejne terminy", ["Wyjątki", "Kalendarz"]))]
        exc = [(to_date(a), to_date(b)) for a, b in EXC_RE.findall(
            section(block, "Wyjątki", ["Kalendarz"]))]
        rule = parse_rule(freq)
        out.append({
            "id": fraction_id(page, freq),
            "frequency": freq,
            "dates": expand(rule, anchor, listed, exc),
        })
    return out


# ---------- pobieranie ----------
def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (kruszyn-app)"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", "replace")


def scrape_live(years):
    merged = {}
    for i, year in enumerate(years):
        for page in PAGES:
            url = URL.format(year=year, page=page)
            try:
                text = html_to_text(fetch(url))
            except Exception as e:  # kolejny rok może jeszcze nie istnieć
                if i == 0:
                    raise SystemExit(f"Błąd pobierania {url}: {e}")
                print(f"(pomijam {url}: {e})", file=sys.stderr)
                continue
            for item in parse_page(page, text):
                cur = merged.setdefault(item["id"], {"frequency": item["frequency"], "dates": []})
                cur["dates"] = sorted(set(cur["dates"]) | set(item["dates"]))
    if not merged:
        raise SystemExit("Nie znaleziono żadnych harmonogramów - zmienił się układ strony?")
    return merged


# Pełny harmonogram 2026 z oficjalnego kalendarza PDF COM-D (wygenerowany 15.11.2026).
# Odzież (02.03, 16.11) i gabaryty/RTV/opony (07.03, 01.08) to jedyne "zbiórki" w PDF;
# podział między nie wywnioskowany ze strony (odzież = najbliższy termin 16.11).
PDF_2026 = {
    "zmieszane": ("Co dwa tygodnie (nieparzyste)",
                  "12.01 26.01 09.02 23.02 09.03 23.03 02.04 20.04 04.05 18.05 01.06 15.06 29.06 "
                  "13.07 27.07 10.08 24.08 07.09 21.09 05.10 19.10 02.11 16.11 30.11 14.12 28.12"),
    "bio": ("Co dwa tygodnie (parzyste)",
            "05.01 19.01 02.02 16.02 02.03 16.03 30.03 13.04 27.04 11.05 25.05 08.06 22.06 "
            "06.07 20.07 03.08 17.08 31.08 14.09 28.09 12.10 26.10 09.11 23.11 07.12 21.12"),
    "plastik": ("Co 4 tygodnie",
                "05.01 02.02 02.03 30.03 27.04 25.05 22.06 20.07 17.08 14.09 12.10 09.11 07.12"),
    "szklo": ("Co 8 tygodni", "19.01 16.03 11.05 06.07 31.08 26.10 21.12"),
    "makulatura": ("Co 8 tygodni", "16.02 13.04 08.06 03.08 28.09 23.11"),
    "odziez": ("odzież i tekstylia 2x w roku", "02.03 16.11"),
    "gabaryty": ("WGB, RTV, OPONY 2x w roku", "07.03 01.08"),
}


def pdf_dates(txt):
    return [dt.date(2026, int(m), int(d)) for d, m in (x.split(".") for x in txt.split())]


def seed_entries():
    return {fid: {"frequency": f, "dates": pdf_dates(t)} for fid, (f, t) in PDF_2026.items()}


# ---------- wynik ----------
def build(entries, mode: str):
    fractions = []
    for fid in ORDER:
        e = entries.get(fid)
        if not e:
            continue
        item = {"id": fid, "label": LABELS[fid], "frequency": e["frequency"],
                "dates": [d.isoformat() if isinstance(d, dt.date) else d for d in e["dates"]]}
        if not item["dates"]:
            item["contact"] = PHONE
        fractions.append(item)
    return {
        "village": "Kruszyn",
        "commune": "Gmina Bolesławiec",
        "source": "http://www.com-d.pl/komunalne/harm/boleslawiec-2026r-gmina/kruszyn",
        "mode": mode,
        "fetched": (dt.date(2026, 11, 15).isoformat() if mode in ("seed", "pdf")
                    else dt.date.today().isoformat()),
        "phone": PHONE,
        "fractions": fractions,
    }


CORE = ["zmieszane", "bio", "plastik", "szklo", "makulatura"]


def check_live(entries):
    """Zabezpieczenie: nie nadpisuj dobrych danych, gdy strona zmieniła układ."""
    missing = [c for c in CORE if c not in entries]
    if missing:
        raise SystemExit(f"Brak frakcji w pobranych danych: {missing} - zmienił się układ strony?")
    if sum(len(e["dates"]) for e in entries.values()) == 0:
        raise SystemExit("Pobrano 0 terminów - nie nadpisuję danych.")


def merge_existing(new: dict, path: str) -> dict:
    """Zachowaj z poprzedniego pliku terminy z bieżącego roku, które już minęły
    (strona podaje tylko przyszłe), a przyszłe bierz z nowego pobrania."""
    p = Path(path)
    if not p.exists():
        return new
    try:
        old = json.loads(p.read_text(encoding="utf-8"))
    except ValueError:
        return new
    today = dt.date.today()
    year_start = f"{today.year}-01-01"
    olds = {f["id"]: f for f in old.get("fractions", [])}
    for f in new["fractions"]:
        o = olds.get(f["id"])
        if not o:
            continue
        past = [d for d in o["dates"] if year_start <= d <= today.isoformat()]
        f["dates"] = sorted(set(past) | set(f["dates"]))
        if f["dates"]:
            f.pop("contact", None)
    return new


def embed(html_path: str, data: dict):
    p = Path(html_path)
    s = p.read_text(encoding="utf-8")
    pat = re.compile(r"(/\*WASTE_DATA_START\*/).*?(/\*WASTE_DATA_END\*/)", re.S)
    if not pat.search(s):
        raise SystemExit("W pliku HTML brak znaczników WASTE_DATA_START/END")
    blob = json.dumps(data, ensure_ascii=False)
    p.write_text(pat.sub(lambda m: m.group(1) + blob + m.group(2), s), encoding="utf-8")


SAMPLE = """Harmonogram dotyczy: odpady zmieszane
Częstotliwość obiorów: Co dwa tygodnie (nieparzyste)
Najbliższy odbiór
poniedziałek, 16.11.2026
(jutro)
Kolejne terminy (najbliższe 5)
- poniedziałek, 30.11.2026 (za 15 dni)
- poniedziałek, 14.12.2026 (za 29 dni)
- poniedziałek, 28.12.2026 (za 43 dni)
Wyjątki
- czwartek, 2.04.2026 ← poniedziałek, 6.04.2026 Poniedziałek Wielkanocny
Kalendarz
"""


def selftest():
    got = parse_page("tnp-odpady-zmieszane", SAMPLE)[0]
    want = ["2026-11-16", "2026-11-30", "2026-12-14", "2026-12-28"]
    assert [d.isoformat() for d in got["dates"]] == want, got
    # reguły ze strony muszą odtworzyć cały kalendarz z PDF
    exc = [(dt.date(2026, 4, 2), dt.date(2026, 4, 6))]
    for fid in ("zmieszane", "bio", "plastik", "szklo", "makulatura"):
        freq, txt = PDF_2026[fid]
        dates = pdf_dates(txt)
        rebuilt = expand(parse_rule(freq), dates[0], [], exc if fid == "zmieszane" else [])
        assert rebuilt == dates, (fid, rebuilt, dates)
    print("selftest OK")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="data/waste.json")
    ap.add_argument("--embed", help="plik HTML, do którego wstawić dane (wersja offline)")
    ap.add_argument("--seed", action="store_true", help="użyj danych startowych zamiast sieci")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.seed:
        data = build(seed_entries(), "pdf")
    else:
        y = dt.date.today().year
        entries = scrape_live([y, y + 1])
        check_live(entries)
        data = merge_existing(build(entries, "live"), a.out)
        data["source"] = URL.format(year=y, page="").rstrip("/")
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    if a.embed:
        embed(a.embed, data)
    print(f"Zapisano {a.out}: " + ", ".join(f"{f['id']}={len(f['dates'])}" for f in data["fractions"]))


if __name__ == "__main__":
    main()
