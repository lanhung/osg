"""Fetch archive extents for frozen FDSN station pairs without realtime claims."""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path


def _parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def summarize_availability(document: dict, network: str, station: str) -> dict:
    rows = [
        row
        for row in document.get("datasources", ())
        if row.get("network") == network
        and row.get("station") == station
        and len(row.get("channel", "")) == 3
        and row["channel"][:2] in {"BH", "LH"}
    ]
    groups: dict[tuple[str, str, str, float], list[dict]] = {}
    for row in rows:
        key = (
            row.get("location", ""),
            row["channel"][:2],
            row.get("quality", ""),
            float(row["samplerate"]),
        )
        groups.setdefault(key, []).append(row)
    triplets = []
    for key, group in sorted(groups.items()):
        components = {row["channel"][2] for row in group}
        if not (
            "Z" in components
            and ({"N", "E"}.issubset(components) or {"1", "2"}.issubset(components))
        ):
            continue
        common_earliest = max(_parse_utc(row["earliest"]) for row in group)
        common_latest = min(_parse_utc(row["latest"]) for row in group)
        triplets.append(
            {
                "location": key[0],
                "band": key[1],
                "quality": key[2],
                "sample_rate_hz": key[3],
                "components": sorted(components),
                "common_earliest": common_earliest.isoformat(),
                "common_latest": common_latest.isoformat(),
                "common_extent_nonempty": common_earliest <= common_latest,
                "all_open": all(row.get("restriction") == "OPEN" for row in group),
                "maximum_timespan_count": max(int(row["timespanCount"]) for row in group),
            }
        )
    return {
        "network": network,
        "station": station,
        "archive_channel_extent_count": len(rows),
        "three_component_archive_extent_count": len(triplets),
        "three_component_archive_extents": triplets,
    }


def build_url(config: dict, network: str, station: str) -> str:
    query = {
        "net": network,
        "sta": station,
        "cha": config["channel"],
        "starttime": config["starttime"],
        "endtime": config["endtime"],
        "format": "json",
        "nodata": 404,
    }
    return "https://service.earthscope.org/fdsnws/availability/1/extent?" + urllib.parse.urlencode(
        query
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--recent-days", type=float, default=7.0)
    parser.add_argument("--timeout", type=float, default=120.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    retrieved_at = datetime.now(UTC)
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for row in config["stations"]:
        network, station = row["network"], row["station"]
        url = build_url(config, network, station)
        request = urllib.request.Request(url, headers={"User-Agent": "oceangravity/0.1"})
        try:
            with urllib.request.urlopen(request, timeout=args.timeout) as response:
                payload = response.read()
                final_url = response.url
                status = response.status
        except urllib.error.HTTPError as error:
            if error.code != 404:
                raise
            results.append({**row, "status": "no_data_404", "requested_url": url})
            continue
        raw_path = args.raw_dir / f"{network}.{station}.json"
        raw_path.write_bytes(payload)
        document = json.loads(payload)
        summary = summarize_availability(document, network, station)
        latest_values = [
            _parse_utc(item["common_latest"])
            for item in summary["three_component_archive_extents"]
            if item["common_extent_nonempty"]
        ]
        latest = max(latest_values) if latest_values else None
        results.append(
            {
                **row,
                "status": "retrieved",
                "requested_url": url,
                "final_url": final_url,
                "http_status": status,
                "raw_path": str(raw_path),
                "size_bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "latest_common_archive_sample": (None if latest is None else latest.isoformat()),
                "archive_recent_within_declared_days": (
                    False
                    if latest is None
                    else (retrieved_at - latest).total_seconds() <= args.recent_days * 86400.0
                ),
                **summary,
            }
        )
    output = {
        "schema_version": 1,
        "retrieved_at_utc": retrieved_at.isoformat(),
        "recent_days": args.recent_days,
        "station_pair_count": len(results),
        "retrieved_pair_count": sum(row["status"] == "retrieved" for row in results),
        "pairs_with_archive_triplet": sum(
            row.get("three_component_archive_extent_count", 0) > 0 for row in results
        ),
        "pairs_with_recent_archive_samples": sum(
            row.get("archive_recent_within_declared_days", False) for row in results
        ),
        "stations": results,
        "warning": (
            "Archive extents and recent samples do not establish continuous "
            "coverage, successful download, usable noise, low latency, or "
            "SeedLink realtime availability."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
