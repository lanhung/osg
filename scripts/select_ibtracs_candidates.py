"""Select auditable South China Sea candidate events from an IBTrACS CSV."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path

EARTH_MEAN_RADIUS_KM = 6371.0088


def _optional_float(value: str | None) -> float | None:
    if value is None or not value.strip():
        return None
    parsed = float(value)
    return parsed if math.isfinite(parsed) else None


def _great_circle_distance_km(
    latitude_a_deg: float,
    longitude_a_deg: float,
    latitude_b_deg: float,
    longitude_b_deg: float,
) -> float:
    latitude_a = math.radians(latitude_a_deg)
    latitude_b = math.radians(latitude_b_deg)
    latitude_delta = latitude_b - latitude_a
    longitude_delta = math.radians(longitude_b_deg - longitude_a_deg)
    haversine = (
        math.sin(latitude_delta / 2.0) ** 2
        + math.cos(latitude_a) * math.cos(latitude_b) * math.sin(longitude_delta / 2.0) ** 2
    )
    return 2.0 * EARTH_MEAN_RADIUS_KM * math.asin(min(1.0, math.sqrt(haversine)))


def select_candidates(input_path: Path, config: dict) -> dict:
    region = config["region"]
    required_basin = config["required_basin"]
    references = tuple(config.get("reference_points", ()))
    for reference in references:
        if not reference["id"].strip():
            raise ValueError("reference point IDs must be non-empty")
        latitude = float(reference["latitude_deg"])
        longitude = float(reference["longitude_deg_east"])
        if not (-90.0 <= latitude <= 90.0 and -180.0 <= longitude <= 180.0):
            raise ValueError("reference point coordinates are out of range")
    grouped: dict[str, list[dict]] = defaultdict(list)
    with input_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required_columns = {"SID", "SEASON", "BASIN", "NAME", "ISO_TIME", "LAT", "LON"}
        if reader.fieldnames is None or not required_columns.issubset(reader.fieldnames):
            raise ValueError("IBTrACS CSV is missing required columns")
        for row in reader:
            sid = row["SID"].strip()
            if not sid or not sid[0].isdigit():
                continue
            if row["BASIN"].strip() != required_basin:
                continue
            latitude = _optional_float(row["LAT"])
            longitude = _optional_float(row["LON"])
            if latitude is None or longitude is None:
                continue
            if not (
                region["minimum_latitude_deg"] <= latitude <= region["maximum_latitude_deg"]
                and region["minimum_longitude_deg_east"]
                <= longitude
                <= region["maximum_longitude_deg_east"]
            ):
                continue
            timestamp = row["ISO_TIME"].strip()
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            grouped[sid].append(
                {
                    "season": int(row["SEASON"]),
                    "name": row["NAME"].strip(),
                    "time": timestamp,
                    "latitude": latitude,
                    "longitude": longitude,
                    "wmo_wind_kt": _optional_float(row.get("WMO_WIND")),
                    "wmo_pressure_mb": _optional_float(row.get("WMO_PRES")),
                    "usa_wind_kt": _optional_float(row.get("USA_WIND")),
                    "usa_pressure_mb": _optional_float(row.get("USA_PRES")),
                }
            )

    minimum_points = int(config["minimum_regional_track_points"])
    events = []
    for sid, points in sorted(grouped.items()):
        if len(points) < minimum_points:
            continue
        points.sort(key=lambda point: point["time"])
        event = {
            "sid": sid,
            "season": points[0]["season"],
            "name": points[0]["name"],
            "regional_entry_time": points[0]["time"],
            "regional_exit_time": points[-1]["time"],
            "regional_track_points": len(points),
            "regional_latitude_range_deg": [
                min(point["latitude"] for point in points),
                max(point["latitude"] for point in points),
            ],
            "regional_longitude_range_deg_east": [
                min(point["longitude"] for point in points),
                max(point["longitude"] for point in points),
            ],
        }
        for output_name, input_name, reducer in (
            ("maximum_wmo_wind_kt", "wmo_wind_kt", max),
            ("minimum_wmo_pressure_mb", "wmo_pressure_mb", min),
            ("maximum_usa_wind_kt", "usa_wind_kt", max),
            ("minimum_usa_pressure_mb", "usa_pressure_mb", min),
        ):
            values = [point[input_name] for point in points if point[input_name] is not None]
            event[output_name] = reducer(values) if values else None
        if references:
            closest = min(
                (
                    _great_circle_distance_km(
                        point["latitude"],
                        point["longitude"],
                        float(reference["latitude_deg"]),
                        float(reference["longitude_deg_east"]),
                    ),
                    reference["id"],
                )
                for point in points
                for reference in references
            )
            event["closest_reference_distance_km"] = closest[0]
            event["closest_reference_point_id"] = closest[1]
        screening = config.get("shortlist_screening")
        if screening is not None:
            failures = []
            wind = event["maximum_usa_wind_kt"]
            if wind is None or wind < float(screening["minimum_maximum_usa_wind_kt"]):
                failures.append("regional_usa_wind_below_or_missing")
            distance = event.get("closest_reference_distance_km")
            if distance is None or distance > float(
                screening["maximum_closest_reference_distance_km"]
            ):
                failures.append("closest_reference_distance_exceeds_limit")
            event["shortlist_screening_passes"] = not failures
            event["shortlist_screening_failures"] = failures
        events.append(event)

    canonical_config = json.dumps(config, sort_keys=True, separators=(",", ":"))
    shortlist = [event for event in events if event.get("shortlist_screening_passes")]
    return {
        "schema_version": 1,
        "selection_id": "paper2-south-china-sea-ibtracs-candidates",
        "input_sha256": hashlib.sha256(input_path.read_bytes()).hexdigest(),
        "config_sha256": hashlib.sha256(canonical_config.encode()).hexdigest(),
        "candidate_count": len(events),
        "shortlist_count": len(shortlist),
        "shortlist_event_ids": [event["sid"] for event in shortlist],
        "reference_points": list(references),
        "shortlist_screening": config.get("shortlist_screening"),
        "events": events,
        "warning": (
            "Candidate status does not imply superconducting-gravimeter coverage "
            "or event suitability."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    result = select_candidates(args.input, config)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
