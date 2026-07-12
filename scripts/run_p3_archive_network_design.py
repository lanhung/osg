"""Freeze a Paper 3 archive/noise network without PEGS waveform claims."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _read(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def _preferred_triplet(station: dict, *, band: str, minimum_rate: float) -> dict | None:
    candidates = [
        row
        for row in station.get("three_component_archive_extents", [])
        if row["band"] == band
        and row["all_open"]
        and row["common_extent_nonempty"]
        and row["sample_rate_hz"] >= minimum_rate
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda row: (_utc(row["common_latest"]), row["sample_rate_hz"]))


def run(config: dict) -> dict:
    if config.get("schema_version") != 1:
        raise ValueError("unsupported Paper 3 network-design schema")
    availability = _read(config["availability_manifest"])
    responses = _read(config["response_manifest"])
    response_ready = {
        (row["network"], row["station"])
        for row in responses["stations"]
        if row["status"] == "retrieved"
        and any(
            epoch["band"] == config["preferred_band"]
            and epoch["full_response_structure_present_for_group"]
            for epoch in row["three_component_response_epochs"]
        )
    }
    cutoff = _utc(config["recent_archive_cutoff_utc"])
    selected = []
    historical = []
    excluded = []
    for station in availability["stations"]:
        key = (station["network"], station["station"])
        triplet = _preferred_triplet(
            station,
            band=config["preferred_band"],
            minimum_rate=float(config["minimum_sample_rate_hz"]),
        )
        row = {
            "network": key[0],
            "station": key[1],
            "station_id": ".".join(key),
            "role": station["role"],
        }
        if key not in response_ready or triplet is None:
            row["reason"] = "response_or_open_three_component_archive_missing"
            excluded.append(row)
        else:
            row["triplet"] = triplet
            historical.append(row)
            if _utc(triplet["common_latest"]) >= cutoff:
                selected.append(row)

    selected.sort(key=lambda row: row["station_id"])
    historical.sort(key=lambda row: row["station_id"])
    excluded.sort(key=lambda row: row["station_id"])
    station_ids = tuple(row["station_id"] for row in selected)
    outage_design = []
    for fraction in map(float, config["outage_fractions"]):
        active_count = max(1, math.ceil((1.0 - fraction) * len(station_ids)))
        combinations = tuple(itertools.combinations(station_ids, active_count))
        outage_design.append(
            {
                "outage_fraction": fraction,
                "active_station_count": active_count,
                "network_variant_count": len(combinations),
                "active_station_sets": combinations,
            }
        )
    common_start = max(_utc(row["triplet"]["common_earliest"]) for row in selected)
    common_end = min(_utc(row["triplet"]["common_latest"]) for row in selected)
    canonical = json.dumps(config, sort_keys=True, separators=(",", ":"))
    return {
        "schema_version": 1,
        "experiment_id": config["experiment_id"],
        "result_class": "open_archive_network_design_not_pegs_detectability",
        "config_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
        "status": (
            "pass"
            if len(selected) >= config["minimum_archive_network_size"] and common_start < common_end
            else "fail"
        ),
        "existing_archive_evaluation_network": selected,
        "historical_archive_sensitivity_network": historical,
        "excluded_metadata_or_unavailable_stations": excluded,
        "common_archive_interval_utc": {
            "start": common_start.isoformat().replace("+00:00", "Z"),
            "end": common_end.isoformat().replace("+00:00", "Z"),
        },
        "outage_design": outage_design,
        "augmented_role_targets": config["augmented_role_targets"],
        "noise_download_ready": len(selected) >= config["minimum_archive_network_size"],
        "operational_warning_ready": False,
        "pegs_detectability_ready": False,
        "interpretation": config["interpretation"],
        "claim_blockers": [
            "archive_availability_is_not_real_time_latency",
            "waveform_response_removal_and_noise_qc_not_yet_run",
            "no_validated_pegs_templates",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run(json.loads(args.config.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
