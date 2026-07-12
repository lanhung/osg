"""Fetch a frozen EarthScope FDSN station/channel inventory with a checksum."""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

ENDPOINT = "https://service.earthscope.org/fdsnws/station/1/query"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--minlatitude", type=float, default=5.0)
    parser.add_argument("--maxlatitude", type=float, default=30.0)
    parser.add_argument("--minlongitude", type=float, default=100.0)
    parser.add_argument("--maxlongitude", type=float, default=130.0)
    parser.add_argument("--channel", default="BH?,LH?")
    parser.add_argument("--starttime", default="2020-01-01T00:00:00")
    parser.add_argument("--endtime", default="2026-07-12T00:00:00")
    parser.add_argument("--timeout", type=float, default=60.0)
    return parser.parse_args()


def build_url(args: argparse.Namespace) -> str:
    query = {
        "format": "text",
        "level": "channel",
        "minlatitude": args.minlatitude,
        "maxlatitude": args.maxlatitude,
        "minlongitude": args.minlongitude,
        "maxlongitude": args.maxlongitude,
        "channel": args.channel,
        "starttime": args.starttime,
        "endtime": args.endtime,
        "includerestricted": "false",
        "nodata": 404,
    }
    return f"{ENDPOINT}?{urllib.parse.urlencode(query)}"


def main() -> int:
    args = parse_args()
    url = build_url(args)
    request = urllib.request.Request(url, headers={"User-Agent": "oceangravity/0.1"})
    with urllib.request.urlopen(request, timeout=args.timeout) as response:  # noqa: S310
        payload = response.read()
        final_url = response.url
        status = response.status
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    metadata = {
        "requested_url": url,
        "final_url": final_url,
        "http_status": status,
        "retrieved_at_utc": datetime.now(UTC).isoformat(),
        "size_bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }
    sidecar = args.output.with_suffix(args.output.suffix + ".metadata.json")
    sidecar.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(metadata, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

