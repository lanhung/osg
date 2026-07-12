"""Summarize FDSN channel text into conservative three-component candidates."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


def summarize_inventory(path: Path) -> dict:
    groups: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="|")
        if reader.fieldnames is None:
            raise ValueError("FDSN inventory has no header")
        reader.fieldnames = [name.lstrip("#").strip() for name in reader.fieldnames]
        required = {
            "Network",
            "Station",
            "Location",
            "Channel",
            "Latitude",
            "Longitude",
            "SampleRate",
            "StartTime",
            "EndTime",
        }
        if not required.issubset(reader.fieldnames):
            raise ValueError("FDSN inventory is missing required channel columns")
        for row in reader:
            channel = row["Channel"].strip()
            if len(channel) != 3 or channel[:2] not in {"BH", "LH"}:
                continue
            key = (
                row["Network"].strip(),
                row["Station"].strip(),
                row["Location"].strip(),
                channel[:2],
                row["StartTime"].strip(),
                row["EndTime"].strip(),
            )
            groups[key].append({name: value.strip() for name, value in row.items()})

    candidates = []
    incomplete = []
    for key, rows in sorted(groups.items()):
        network, station, location, band, start, end = key
        components = sorted({row["Channel"][2] for row in rows})
        has_triplet = "Z" in components and (
            {"N", "E"}.issubset(components) or {"1", "2"}.issubset(components)
        )
        record = {
            "network": network,
            "station": station,
            "location": location,
            "band": band,
            "start_time": start,
            "end_time": end,
            "components": components,
            "latitude_deg": float(rows[0]["Latitude"]),
            "longitude_deg": float(rows[0]["Longitude"]),
            "sample_rates_hz": sorted({float(row["SampleRate"]) for row in rows}),
            "scalar_sensitivity_present_for_all_channels": all(
                bool(row.get("Scale", "")) and bool(row.get("ScaleUnits", "")) for row in rows
            ),
            "full_response_verified": False,
        }
        (candidates if has_triplet else incomplete).append(record)
    open_ended = [record for record in candidates if not record["end_time"]]
    return {
        "schema_version": 1,
        "inventory_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "candidate_epoch_count": len(candidates),
        "incomplete_epoch_count": len(incomplete),
        "open_ended_candidate_epoch_count": len(open_ended),
        "open_ended_unique_network_station_count": len(
            {(record["network"], record["station"]) for record in open_ended}
        ),
        "open_ended_networks": sorted({record["network"] for record in open_ended}),
        "three_component_candidates": candidates,
        "incomplete_channel_epochs": incomplete,
        "warning": (
            "An open-ended channel epoch does not establish current operation. "
            "Channel metadata and scalar sensitivity do not establish waveform "
            "availability, full response, real-time latency, licence, or usable "
            "noise quality."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = summarize_inventory(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
