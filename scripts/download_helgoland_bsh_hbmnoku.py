"""Download and inventory the registered Helgoland BSH-HBMnoku SSH inputs."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import time
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from typing import NamedTuple

import h5py

ROOT = Path(__file__).resolve().parents[1]


class Download(NamedTuple):
    grid: str
    cycle_utc: str
    url: str
    destination: Path


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def build_downloads(manifest: dict, output_dir: Path | None = None) -> tuple[Download, ...]:
    entry = next(row for row in manifest["inputs"] if row["id"] == "bsh-hbmnoku")
    output_root = output_dir or Path(entry["remote_directory"])
    cycle = parse_utc(entry["registered_window"]["start_utc"])
    end = parse_utc(entry["registered_window"]["end_utc"])
    step = timedelta(hours=int(entry["analysis_cycle_hours"]))
    downloads = []
    while cycle <= end:
        for grid in entry["grids"]:
            url = grid["download_pattern"].format(cycle=cycle)
            downloads.append(
                Download(
                    grid=grid["id"],
                    cycle_utc=cycle.isoformat().replace("+00:00", "Z"),
                    url=url,
                    destination=output_root / grid["id"] / url.rsplit("/", 1)[-1],
                )
            )
        cycle += step
    expected = int(entry["expected_file_count"])
    if len(downloads) != expected or len({row.url for row in downloads}) != expected:
        raise ValueError("registered BSH-HBMnoku file count is inconsistent")
    return tuple(downloads)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_netcdf(path: Path) -> None:
    with path.open("rb") as stream:
        magic = stream.read(8)
    if not (magic.startswith(b"CDF") or magic == b"\x89HDF\r\n\x1a\n"):
        raise ValueError(f"not a recognized NetCDF container: {path}")
    if magic == b"\x89HDF\r\n\x1a\n":
        with h5py.File(path, "r") as dataset:
            if "elev" not in dataset:
                raise ValueError(f"missing elev dataset: {path}")


def fetch(row: Download, retries: int = 4) -> dict:
    row.destination.parent.mkdir(parents=True, exist_ok=True)
    if row.destination.exists():
        try:
            validate_netcdf(row.destination)
        except (OSError, ValueError):
            row.destination.unlink()
    if not row.destination.exists():
        temporary = row.destination.with_suffix(row.destination.suffix + ".part")
        error: Exception | None = None
        for attempt in range(retries):
            try:
                request = urllib.request.Request(
                    row.url, headers={"User-Agent": "ocean-gravity-reproduction/1"}
                )
                with (
                    urllib.request.urlopen(request, timeout=120) as response,
                    temporary.open("wb") as stream,
                ):
                    while block := response.read(1024 * 1024):
                        stream.write(block)
                validate_netcdf(temporary)
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
        "grid": row.grid,
        "cycle_utc": row.cycle_utc,
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
        files = sorted(
            executor.map(fetch, downloads),
            key=lambda row: (row["cycle_utc"], row["grid"]),
        )
    canonical = json.dumps(files, sort_keys=True, separators=(",", ":")).encode()
    result = {
        "schema_version": 1,
        "file_count": len(files),
        "total_bytes": sum(row["bytes"] for row in files),
        "inventory_sha256": hashlib.sha256(canonical).hexdigest(),
        "files": files,
    }
    inventory_path = downloads[0].destination.parents[1] / "inventory.json"
    inventory_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in result.items() if key != "files"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
