#!/usr/bin/env python3
"""Perform one bounded SeedLink packet-recency audit for Paper 3 stations."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from obspy import UTCDateTime
from obspy.clients.seedlink.basic_client import Client


def summarize_stream(stream, query_end: UTCDateTime) -> dict:
    if not stream:
        return {
            "status": "no_packets",
            "trace_count": 0,
            "latest_end_utc": None,
            "lag_seconds": None,
        }
    latest = max(trace.stats.endtime for trace in stream)
    earliest = min(trace.stats.starttime for trace in stream)
    return {
        "status": "packets_received",
        "trace_count": len(stream),
        "earliest_start_utc": earliest.isoformat(),
        "latest_end_utc": latest.isoformat(),
        "lag_seconds": round(float(query_end - latest), 6),
        "sample_rates_hz": sorted({float(trace.stats.sampling_rate) for trace in stream}),
        "total_samples": sum(int(trace.stats.npts) for trace in stream),
    }


def audit(config_path: Path) -> dict:
    config_bytes = config_path.read_bytes()
    config = json.loads(config_bytes)
    query_end = UTCDateTime()
    query_start = query_end - 60 * config["lookback_minutes"]
    results = []
    for selection in config["streams"]:
        row = dict(selection)
        try:
            client = Client(
                config["endpoint"],
                port=config["port"],
                timeout=config["timeout_seconds"],
            )
            stream = client.get_waveforms(
                selection["network"],
                selection["station"],
                selection["location"],
                selection["channel"],
                query_start,
                query_end,
            )
            row.update(summarize_stream(stream, query_end))
        except Exception as error:  # network/protocol failures are audit results
            row.update(status="query_error", error=f"{type(error).__name__}: {error}")
        results.append(row)
    return {
        "schema_version": 1,
        "audit_id": config["audit_id"],
        "generated_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "config_sha256": hashlib.sha256(config_bytes).hexdigest(),
        "endpoint": f"{config['endpoint']}:{config['port']}",
        "query_start_utc": query_start.isoformat(),
        "query_end_utc": query_end.isoformat(),
        "streams": results,
        "summary": {
            "requested": len(results),
            "packets_received": sum(row["status"] == "packets_received" for row in results),
            "no_packets": sum(row["status"] == "no_packets" for row in results),
            "query_errors": sum(row["status"] == "query_error" for row in results),
        },
        "interpretation": config["interpretation"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.config)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
