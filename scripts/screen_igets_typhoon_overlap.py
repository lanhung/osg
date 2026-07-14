"""Screen public IGETS sensor epochs against IBTrACS tracks for data inquiries."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

EARTH_MEAN_RADIUS_KM = 6371.0088


def _float(value: str | None) -> float | None:
    if value is None or not value.strip():
        return None
    parsed = float(value)
    return parsed if math.isfinite(parsed) else None


def _distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = phi2 - phi1
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * EARTH_MEAN_RADIUS_KM * math.asin(min(1.0, math.sqrt(a)))


def screen(station_inventory: dict, ibtracs_path: Path, config: dict) -> dict:
    region = config["station_region"]
    rules = config["station_rules"]
    candidates: dict[str, dict] = {}
    for row in station_inventory["stations"]:
        if rules["require_open_ended_sensor_epoch"] and not row["active_in_public_table"]:
            continue
        if not (
            region["minimum_latitude_deg"] <= row["latitude_deg"] <= region["maximum_latitude_deg"]
            and region["minimum_longitude_deg_east"]
            <= row["longitude_deg_east"]
            <= region["maximum_longitude_deg_east"]
        ):
            continue
        key = row["station"] if rules["deduplicate_by_station_name"] else row["sensor"]
        entry = candidates.setdefault(
            key,
            {
                "station": row["station"],
                "latitude_deg": row["latitude_deg"],
                "longitude_deg_east": row["longitude_deg_east"],
                "active_sensors": [],
            },
        )
        entry["active_sensors"].append(row["sensor"])

    event_rules = config["event_screen"]
    events: dict[str, list[dict]] = defaultdict(list)
    with ibtracs_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"SID", "SEASON", "BASIN", "NAME", "ISO_TIME", "LAT", "LON"}
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise ValueError("IBTrACS CSV is missing required columns")
        for row in reader:
            if row["BASIN"].strip() != event_rules["required_basin"]:
                continue
            if not row["SEASON"].strip().isdigit():
                continue
            season = int(row["SEASON"])
            if season < int(event_rules["minimum_season"]):
                continue
            latitude, longitude = _float(row["LAT"]), _float(row["LON"])
            if latitude is None or longitude is None:
                continue
            events[row["SID"].strip()].append(
                {
                    "season": season,
                    "name": row["NAME"].strip(),
                    "time": row["ISO_TIME"].strip(),
                    "latitude_deg": latitude,
                    "longitude_deg_east": longitude,
                    "usa_wind_kt": _float(row.get("USA_WIND")),
                }
            )

    matches = []
    for station in candidates.values():
        station_matches = []
        for sid, points in events.items():
            winds = [p["usa_wind_kt"] for p in points if p["usa_wind_kt"] is not None]
            maximum_wind = max(winds) if winds else None
            if maximum_wind is None or maximum_wind < event_rules["minimum_maximum_usa_wind_kt"]:
                continue
            closest = min(
                (
                    _distance_km(
                        station["latitude_deg"],
                        station["longitude_deg_east"],
                        point["latitude_deg"],
                        point["longitude_deg_east"],
                    ),
                    point,
                )
                for point in points
            )
            if closest[0] > event_rules["maximum_closest_track_distance_km"]:
                continue
            station_matches.append(
                {
                    "sid": sid,
                    "name": points[0]["name"],
                    "season": points[0]["season"],
                    "maximum_usa_wind_kt": maximum_wind,
                    "closest_track_distance_km": closest[0],
                    "closest_track_time": closest[1]["time"],
                }
            )
        station_matches.sort(key=lambda item: (item["closest_track_distance_km"], item["sid"]))
        matches.append(
            {
                **station,
                "event_match_count": len(station_matches),
                "events": station_matches,
            }
        )
    matches.sort(key=lambda item: (-item["event_match_count"], item["station"]))
    canonical_config = json.dumps(config, sort_keys=True, separators=(",", ":"))
    return {
        "schema_version": 1,
        "screen_id": "igets-public-station-ibtracs-acquisition-priority",
        "station_inventory_sha256": hashlib.sha256(
            json.dumps(station_inventory, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "ibtracs_sha256": hashlib.sha256(ibtracs_path.read_bytes()).hexdigest(),
        "config_sha256": hashlib.sha256(canonical_config.encode()).hexdigest(),
        "candidate_station_count": len(matches),
        "stations_with_matches": sum(item["event_match_count"] > 0 for item in matches),
        "stations": matches,
        "warning": config["interpretation"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--station-inventory", type=Path, required=True)
    parser.add_argument("--ibtracs", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    inventory = json.loads(args.station_inventory.read_text(encoding="utf-8"))
    config = json.loads(args.config.read_text(encoding="utf-8"))
    result = screen(inventory, args.ibtracs, config)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
