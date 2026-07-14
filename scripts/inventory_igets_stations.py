"""Create a checksummed inventory from the official public IGETS station table."""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
from html.parser import HTMLParser
from pathlib import Path


class _StationTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._in_cell = False
        self._cell_parts: list[str] = []
        self._row: list[dict[str, str | None]] = []
        self.rows: list[list[dict[str, str | None]]] = []
        self._href: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "td":
            self._in_cell = True
            self._cell_parts = []
            self._href = None
        elif tag == "a" and self._in_cell:
            self._href = dict(attrs).get("href")

    def handle_data(self, data: str) -> None:
        if self._in_cell:
            self._cell_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "td" and self._in_cell:
            self._row.append(
                {"text": " ".join("".join(self._cell_parts).split()), "href": self._href}
            )
            self._in_cell = False
        elif tag == "tr":
            if self._row:
                self.rows.append(self._row)
            self._row = []


def parse_station_table(html: bytes) -> list[dict]:
    parser = _StationTableParser()
    parser.feed(html.decode("utf-8", errors="replace"))
    stations = []
    for row in parser.rows:
        if len(row) != 8:
            continue
        values = [cell["text"] for cell in row]
        try:
            latitude = float(values[2])
            longitude = float(values[3])
            height = float(values[4])
            start_year = int(values[5])
            end_year = int(values[6]) if values[6] else None
        except (TypeError, ValueError):
            continue
        stations.append(
            {
                "station": values[0],
                "sensor": values[1],
                "latitude_deg": latitude,
                "longitude_deg_east": longitude,
                "height_msl_m": height,
                "start_year": start_year,
                "end_year": end_year,
                "active_in_public_table": end_year is None,
                "contact": values[7],
                "doi_or_station_url": row[0]["href"],
            }
        )
    if not stations:
        raise ValueError("no IGETS station rows parsed")
    return stations


def build_inventory(html: bytes, source_url: str, retrieved_utc: str) -> dict:
    stations = parse_station_table(html)
    return {
        "schema_version": 1,
        "inventory_id": "official-public-igets-station-table",
        "source_url": source_url,
        "retrieved_utc": retrieved_utc,
        "source_sha256": hashlib.sha256(html).hexdigest(),
        "sensor_epoch_count": len(stations),
        "station_count": len({row["station"] for row in stations}),
        "stations": stations,
        "warning": (
            "The public station table is not authenticated file availability. "
            "Remote paths, event coverage, headers, calibration and terms must be "
            "inventoried after login before data selection."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="https://isdc.gfz.de/igets-data-base/")
    parser.add_argument("--retrieved-utc", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    request = urllib.request.Request(args.url, headers={"User-Agent": "osg-research/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        html = response.read()
    result = build_inventory(html, args.url, args.retrieved_utc)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
