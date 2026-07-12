"""Fetch a versioned IBTrACS CSV and write immutable retrieval metadata."""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
from datetime import UTC, datetime
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=120.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    url = manifest["download_url"]
    request = urllib.request.Request(url, headers={"User-Agent": "oceangravity/0.1"})
    with urllib.request.urlopen(request, timeout=args.timeout) as response:  # noqa: S310
        payload = response.read()
        final_url = response.url
        status = response.status
        last_modified = response.headers.get("Last-Modified")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    metadata = {
        "dataset": manifest["dataset"],
        "release": manifest["release"],
        "requested_url": url,
        "final_url": final_url,
        "http_status": status,
        "http_last_modified": last_modified,
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
