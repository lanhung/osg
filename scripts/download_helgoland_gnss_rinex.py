"""Download and inventory the registered Helgoland BKG RINEX inputs."""

from __future__ import annotations

import argparse
import concurrent.futures
import gzip
import hashlib
import json
import os
import time
import urllib.request
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[1]


class Download(NamedTuple):
    url: str
    destination: Path


def build_downloads(manifest: dict, output_dir: Path | None = None) -> tuple[Download, ...]:
    entry = next(row for row in manifest["inputs"] if row["id"] == "helg-hel2-gnss")
    source = entry["raw_rinex"]
    destination_root = output_dir or Path(source["remote_directory"])
    first, last = source["day_of_year_range_inclusive"]
    downloads = []
    for station in entry["stations"]:
        for day_of_year in range(int(first), int(last) + 1):
            filename = source["file_pattern"].format(station=station["id"], doy=day_of_year)
            downloads.append(
                Download(
                    url=f"{source['base_url']}/{day_of_year:03d}/{filename}",
                    destination=destination_root / filename,
                )
            )
    expected = int(source["expected_file_count"])
    if len(downloads) != expected or len({row.url for row in downloads}) != expected:
        raise ValueError("registered GNSS file count is inconsistent")
    return tuple(downloads)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_gzip(path: Path) -> None:
    if path.stat().st_size == 0:
        raise ValueError(f"empty download: {path}")
    with gzip.open(path, "rb") as stream:
        if not stream.read(1):
            raise ValueError(f"empty gzip payload: {path}")


def fetch(row: Download, retries: int = 4) -> dict:
    row.destination.parent.mkdir(parents=True, exist_ok=True)
    if row.destination.exists():
        validate_gzip(row.destination)
    else:
        temporary = row.destination.with_suffix(row.destination.suffix + ".part")
        error: Exception | None = None
        for attempt in range(retries):
            try:
                request = urllib.request.Request(
                    row.url, headers={"User-Agent": "ocean-gravity-reproduction/1"}
                )
                with (
                    urllib.request.urlopen(request, timeout=90) as response,
                    temporary.open("wb") as stream,
                ):
                    while block := response.read(1024 * 1024):
                        stream.write(block)
                validate_gzip(temporary)
                os.replace(temporary, row.destination)
                break
            except Exception as exc:  # network failures need bounded retries
                error = exc
                temporary.unlink(missing_ok=True)
                if attempt + 1 < retries:
                    time.sleep(2**attempt)
        else:
            raise RuntimeError(f"failed to download {row.url}") from error
    return {
        "filename": row.destination.name,
        "bytes": row.destination.stat().st_size,
        "sha256": sha256(row.destination),
        "source_url": row.url,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "data/manifests/helgoland_reproduction_inputs.json",
    )
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--workers", type=int, default=8)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = json.loads(args.manifest.read_text())
    downloads = build_downloads(manifest, args.output_dir)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        files = sorted(executor.map(fetch, downloads), key=lambda row: row["filename"])
    canonical = json.dumps(files, sort_keys=True, separators=(",", ":")).encode()
    result = {
        "schema_version": 1,
        "file_count": len(files),
        "total_bytes": sum(row["bytes"] for row in files),
        "inventory_sha256": hashlib.sha256(canonical).hexdigest(),
        "files": files,
    }
    inventory_path = downloads[0].destination.parent / "inventory.json"
    inventory_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in result.items() if key != "files"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
