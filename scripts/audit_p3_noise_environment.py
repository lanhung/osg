#!/usr/bin/env python3
"""Audit earthquake and IBTrACS overlap for frozen Paper 3 noise windows."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import urllib.parse
import urllib.request
from datetime import UTC, datetime, timedelta
from pathlib import Path


def parse_utc(value: str) -> datetime:
    value = value.strip().replace(" ", "T")
    if not value.endswith("Z") and "+" not in value[10:]:
        value += "Z"
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_km = 6371.0088
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = phi2 - phi1
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * radius_km * math.asin(math.sqrt(a))


def interval_overlaps(
    start_a: datetime, end_a: datetime, start_b: datetime, end_b: datetime
) -> bool:
    return start_a <= end_b and start_b <= end_a


def event_station_candidate(
    event_time: datetime,
    magnitude: float,
    distance_km: float,
    window_start: datetime,
    window_end: datetime,
    rules: dict,
) -> tuple[bool, str | None, datetime, datetime]:
    fast, slow = (
        max(rules["surface_wave_velocity_range_km_s"]),
        min(rules["surface_wave_velocity_range_km_s"]),
    )
    arrival_start = event_time + timedelta(seconds=distance_km / fast)
    arrival_end = event_time + timedelta(seconds=distance_km / slow)
    coda_end = arrival_end + timedelta(hours=rules["post_arrival_coda_hours"])
    magnitude_reason = None
    if magnitude >= rules["global_minimum_magnitude"]:
        magnitude_reason = "global_magnitude_rule"
    elif (
        magnitude >= rules["regional_minimum_magnitude"]
        and distance_km <= rules["regional_maximum_distance_km"]
    ):
        magnitude_reason = "regional_magnitude_distance_rule"
    overlaps = interval_overlaps(arrival_start, coda_end, window_start, window_end)
    return magnitude_reason is not None and overlaps, magnitude_reason, arrival_start, coda_end


def load_windows(repo: Path, paths: list[str]) -> list[dict]:
    windows = []
    for relpath in paths:
        manifest = json.loads((repo / relpath).read_text())
        windows.extend(manifest["windows"])
    return windows


def fetch_catalog(
    base_url: str, start: datetime, end: datetime, minimum_magnitude: float
) -> tuple[str, bytes]:
    params = {
        "format": "geojson",
        "starttime": start.isoformat().replace("+00:00", "Z"),
        "endtime": end.isoformat().replace("+00:00", "Z"),
        "minmagnitude": str(minimum_magnitude),
        "orderby": "time-asc",
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={"User-Agent": "osg-paper3-environment-audit/1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return url, response.read()


def audit(repo: Path, config_path: Path, raw_dir: Path) -> dict:
    config_bytes = config_path.read_bytes()
    config = json.loads(config_bytes)
    windows = load_windows(repo, config["input_manifests"])
    ibtracs = json.loads((repo / config["ibtracs"]["candidate_manifest"]).read_text())["events"]
    raw_dir.mkdir(parents=True, exist_ok=True)
    results = []
    rules = config["earthquake_catalog"]["candidate_rules"]

    for window in windows:
        start, end = parse_utc(window["start_utc"]), parse_utc(window["end_utc"])
        query_start = start - timedelta(hours=config["earthquake_catalog"]["lookback_hours"])
        query_url, raw = fetch_catalog(
            config["earthquake_catalog"]["base_url"],
            query_start,
            end,
            config["earthquake_catalog"]["minimum_query_magnitude"],
        )
        raw_path = raw_dir / f"{window['window_id']}.geojson"
        raw_path.write_bytes(raw)
        catalog = json.loads(raw)
        candidates = []
        for feature in catalog["features"]:
            props, coords = feature["properties"], feature["geometry"]["coordinates"]
            if props.get("mag") is None:
                continue
            event_time = datetime.fromtimestamp(props["time"] / 1000, tz=UTC)
            station_hits = []
            for station in config["stations"]:
                distance = haversine_km(
                    station["latitude_deg"], station["longitude_deg"], coords[1], coords[0]
                )
                hit, reason, arrival_start, coda_end = event_station_candidate(
                    event_time, props["mag"], distance, start, end, rules
                )
                if hit:
                    station_hits.append(
                        {
                            "station": f"{station['network']}.{station['station']}",
                            "distance_km": round(distance, 3),
                            "rule": reason,
                            "predicted_surface_arrival_start_utc": (
                                arrival_start.isoformat().replace("+00:00", "Z")
                            ),
                            "conservative_coda_end_utc": coda_end.isoformat().replace(
                                "+00:00", "Z"
                            ),
                        }
                    )
            if station_hits:
                candidates.append(
                    {
                        "event_id": feature["id"],
                        "time_utc": event_time.isoformat().replace("+00:00", "Z"),
                        "magnitude": props["mag"],
                        "place": props.get("place"),
                        "detail_url": props.get("url"),
                        "station_hits": station_hits,
                    }
                )

        storms = []
        for event in ibtracs:
            entry, exit_ = (
                parse_utc(event["regional_entry_time"]),
                parse_utc(event["regional_exit_time"]),
            )
            if interval_overlaps(start, end, entry, exit_):
                storms.append(
                    {
                        "sid": event["sid"],
                        "name": event["name"],
                        "regional_entry_time": event["regional_entry_time"],
                        "regional_exit_time": event["regional_exit_time"],
                        "maximum_usa_wind_kt": event["maximum_usa_wind_kt"],
                        "closest_reference_distance_km": event["closest_reference_distance_km"],
                    }
                )
        passed_catalog_layers = not candidates and not storms
        results.append(
            {
                "window_id": window["window_id"],
                "start_utc": window["start_utc"],
                "end_utc": window["end_utc"],
                "usgs_query_url": query_url,
                "usgs_raw_sha256": hashlib.sha256(raw).hexdigest(),
                "usgs_event_count_m4plus": len(catalog["features"]),
                "earthquake_candidates": candidates,
                "ibtracs_regional_overlaps": storms,
                "catalogue_layers_pass": passed_catalog_layers,
                "environment_label_status": "pending_weather_sea_state_and_waveform_review",
            }
        )

    return {
        "schema_version": 1,
        "audit_id": config["audit_id"],
        "generated_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "config_sha256": hashlib.sha256(config_bytes).hexdigest(),
        "raw_data_policy": (
            "USGS GeoJSON retained outside Git; query URLs and SHA-256 hashes retained here."
        ),
        "windows": results,
        "summary": {
            "window_count": len(results),
            "catalogue_layers_pass_count": sum(item["catalogue_layers_pass"] for item in results),
            "earthquake_candidate_window_count": sum(
                bool(item["earthquake_candidates"]) for item in results
            ),
            "ibtracs_overlap_window_count": sum(
                bool(item["ibtracs_regional_overlaps"]) for item in results
            ),
            "quiet_label_count": 0,
        },
        "remaining_gate": config["final_label_gate"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--config", type=Path, default=Path("configs/paper3/noise_environment_audit.json")
    )
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config_path = args.config if args.config.is_absolute() else args.repo / args.config
    result = audit(args.repo, config_path, args.raw_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
