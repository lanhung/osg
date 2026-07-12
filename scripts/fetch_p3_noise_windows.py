"""Fetch predeclared Paper 3 MiniSEED noise-window candidates."""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def request_url(base_url: str, station: dict, window: dict, channel_band: str) -> str:
    """Build one FDSN wildcard URL, encoding an empty location as ``--``."""

    parameters = {
        "net": station["network"],
        "sta": station["station"],
        "loc": station["location"] or "--",
        "cha": f"{channel_band}?",
        "starttime": window["start_utc"],
        "endtime": window["end_utc"],
        "nodata": "404",
    }
    return f"{base_url}?{urllib.parse.urlencode(parameters)}"


def build_requests(document: dict) -> tuple[dict, ...]:
    if document.get("schema_version") != 1:
        raise ValueError("unsupported noise-window request schema")
    base_url = document["source"]["base_url"]
    rows = []
    for window in document["windows"]:
        for station in document["stations"]:
            parameters = {
                "net": station["network"],
                "sta": station["station"],
                "loc": station["location"],
                "cha": ",".join(station["channels"]),
                "starttime": window["start_utc"],
                "endtime": window["end_utc"],
                "nodata": "404",
            }
            filename = (
                f"{station['network']}.{station['station']}."
                f"{station['location'].replace('--', 'blank')}.LH3.mseed"
            )
            rows.append(
                {
                    "window_id": window["window_id"],
                    "split_role": window["split_role"],
                    "label_status": window["label_status"],
                    "network": station["network"],
                    "station": station["station"],
                    "location": station["location"],
                    "channels": station["channels"],
                    "start_utc": window["start_utc"],
                    "end_utc": window["end_utc"],
                    "requested_url": f"{base_url}?{urllib.parse.urlencode(parameters)}",
                    "raw_path": str(Path(document["raw_root"]) / window["window_id"] / filename),
                }
            )
    return tuple(rows)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fetch(document: dict, *, timeout_s: float = 120.0) -> dict:
    results = []
    for row in build_requests(document):
        output = ROOT / row["raw_path"]
        output.parent.mkdir(parents=True, exist_ok=True)
        request = urllib.request.Request(
            row["requested_url"],
            headers={"User-Agent": "ocean-gravity-research/1.0 (registered compact audit)"},
        )
        result = dict(row)
        try:
            with urllib.request.urlopen(request, timeout=timeout_s) as response:
                payload = response.read()
                result["http_status"] = response.status
                result["final_url"] = response.url
        except urllib.error.HTTPError as error:
            result.update(status="http_error", http_status=error.code, error=str(error))
        except (TimeoutError, urllib.error.URLError) as error:
            result.update(status="request_error", http_status=None, error=str(error))
        else:
            output.write_bytes(payload)
            result.update(
                status="retrieved",
                size_bytes=len(payload),
                sha256=_sha256(output),
            )
        results.append(result)
    return {
        "schema_version": 1,
        "manifest_id": document["manifest_id"],
        "retrieved_at_utc": datetime.now(UTC).isoformat(),
        "request_count": len(results),
        "retrieved_count": sum(row["status"] == "retrieved" for row in results),
        "requests": results,
        "raw_redistribution": document["source"]["redistribution"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout-s", type=float, default=120.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    document = json.loads(args.manifest.read_text(encoding="utf-8"))
    result = fetch(document, timeout_s=args.timeout_s)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
