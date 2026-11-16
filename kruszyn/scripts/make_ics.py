#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tworzy kalendarz .ics z terminami wywozu śmieci na podstawie data/waste.json.

Użycie (z głównego folderu repozytorium):
  python3 scripts/make_ics.py
Wynik: data/kruszyn-smieci.ics (można go zasubskrybować w kalendarzu telefonu).
"""
import datetime as dt
import json
import sys
from pathlib import Path

SRC = Path("data/waste.json")
OUT = Path("data/kruszyn-smieci.ics")
# Stały znacznik czasu, żeby plik zmieniał się tylko wtedy, gdy zmienią się terminy.
STAMP = "20260101T000000Z"


def esc(t: str) -> str:
    return t.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def fold(line: str) -> str:
    """Zawijanie linii do 75 bajtów (wymóg formatu iCalendar), bez cięcia znaków UTF-8."""
    parts, b, limit = [], line.encode("utf-8"), 75
    while len(b) > limit:
        cut = limit
        while (b[cut] & 0xC0) == 0x80:
            cut -= 1
        parts.append(b[:cut].decode("utf-8"))
        b, limit = b[cut:], 74
    parts.append(b.decode("utf-8"))
    return "\r\n ".join(parts)


def main() -> None:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    by_date: dict[str, list[str]] = {}
    for f in data["fractions"]:
        for d in f["dates"]:
            by_date.setdefault(d, []).append(f["label"].lower())

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Kruszyn//Wywoz smieci//PL",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Wywóz śmieci – Kruszyn",
        "REFRESH-INTERVAL;VALUE=DURATION:P1D",
        "X-PUBLISHED-TTL:P1D",
    ]
    for d in sorted(by_date):
        start = dt.date.fromisoformat(d)
        end = start + dt.timedelta(days=1)
        what = ", ".join(by_date[d])
        lines += [
            "BEGIN:VEVENT",
            f"UID:{d}-smieci@kruszyn",
            f"DTSTAMP:{STAMP}",
            f"DTSTART;VALUE=DATE:{start:%Y%m%d}",
            f"DTEND;VALUE=DATE:{end:%Y%m%d}",
            f"SUMMARY:{esc('Wywóz śmieci: ' + what)}",
            f"DESCRIPTION:{esc('Odbiór: ' + what + '. Pamiętaj o wystawieniu pojemników.')}",
            "TRANSP:TRANSPARENT",
            "BEGIN:VALARM",
            "ACTION:DISPLAY",
            f"DESCRIPTION:{esc('Jutro wywóz śmieci: ' + what)}",
            "TRIGGER:-PT6H",  # 18:00 dzień wcześniej
            "END:VALARM",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    OUT.write_bytes(("\r\n".join(fold(l) for l in lines) + "\r\n").encode("utf-8"))
    print(f"Zapisano {OUT}: {len(by_date)} terminów")


if __name__ == "__main__":
    sys.exit(main())
