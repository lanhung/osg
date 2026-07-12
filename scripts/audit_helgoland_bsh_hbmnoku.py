"""Audit BSH-HBMnoku file structure and time coverage for Helgoland."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import xarray as xr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from download_helgoland_bsh_hbmnoku import build_downloads, parse_utc  # noqa: E402


def audit_time_axis(
    actual: np.ndarray,
    cycle: datetime,
    steps: int,
    first_offset_minutes: int,
    last_offset_minutes: int,
    maximum_adjustment_seconds: float,
) -> tuple[np.ndarray, float]:
    expected = np.arange(
        np.datetime64(cycle.replace(tzinfo=None), "ns") + np.timedelta64(first_offset_minutes, "m"),
        np.datetime64(cycle.replace(tzinfo=None), "ns")
        + np.timedelta64(last_offset_minutes + first_offset_minutes, "m"),
        np.timedelta64(first_offset_minutes, "m"),
    )
    if expected.size != steps or actual.size != steps:
        raise ValueError("unexpected number of model time steps")
    error_ns = np.abs(actual.astype("datetime64[ns]").astype(np.int64) - expected.astype(np.int64))
    maximum_error_seconds = float(error_ns.max(initial=0)) / 1e9
    if maximum_error_seconds > maximum_adjustment_seconds:
        raise ValueError("model timestamp exceeds canonicalization tolerance")
    return expected, maximum_error_seconds


def coordinate_hash(values: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(values).tobytes()).hexdigest()


def audit(manifest: dict, output_dir: Path | None = None) -> dict:
    entry = next(row for row in manifest["inputs"] if row["id"] == "bsh-hbmnoku")
    payload = entry["file_payload"]
    tolerance = float(entry["timestamp_canonicalization"]["maximum_allowed_adjustment_seconds"])
    start = parse_utc(entry["registered_window"]["start_utc"])
    end = parse_utc(entry["registered_window"]["end_utc"])
    downloads = build_downloads(manifest, output_dir)
    grid_state: dict[str, dict] = {}
    maximum_error = 0.0
    missing = []
    for row in downloads:
        if not row.destination.exists():
            missing.append(str(row.destination))
            continue
        with xr.open_dataset(row.destination, engine="h5netcdf", mask_and_scale=False) as dataset:
            if payload["variable"] not in dataset:
                raise ValueError(f"missing elev variable: {row.destination}")
            elevation = dataset[payload["variable"]]
            if elevation.dims != ("time", "lat", "lon"):
                raise ValueError(f"unexpected elev dimensions: {row.destination}")
            if elevation.attrs.get("standard_name") != payload["variable_standard_name"]:
                raise ValueError(f"unexpected elev standard_name: {row.destination}")
            if elevation.attrs.get("units") != payload["unit"]:
                raise ValueError(f"unexpected elev unit: {row.destination}")
            canonical, error = audit_time_axis(
                dataset.time.values,
                parse_utc(row.cycle_utc),
                int(payload["time_steps"]),
                int(payload["first_step_offset_minutes"]),
                int(payload["last_step_offset_minutes"]),
                tolerance,
            )
            maximum_error = max(maximum_error, error)
            state = grid_state.setdefault(
                row.grid,
                {
                    "files": 0,
                    "shape": list(elevation.shape[1:]),
                    "latitude_sha256": coordinate_hash(dataset.lat.values),
                    "longitude_sha256": coordinate_hash(dataset.lon.values),
                    "canonical_times": [],
                },
            )
            if state["shape"] != list(elevation.shape[1:]):
                raise ValueError(f"changing spatial shape in {row.grid}")
            if state["latitude_sha256"] != coordinate_hash(dataset.lat.values):
                raise ValueError(f"changing latitude coordinates in {row.grid}")
            if state["longitude_sha256"] != coordinate_hash(dataset.lon.values):
                raise ValueError(f"changing longitude coordinates in {row.grid}")
            state["files"] += 1
            state["canonical_times"].extend(canonical.tolist())
    if missing:
        raise FileNotFoundError(f"missing {len(missing)} registered model files")
    rendered_grids = {}
    for grid, state in sorted(grid_state.items()):
        times = np.asarray(state.pop("canonical_times"), dtype="datetime64[ns]")
        if np.any(np.diff(times.astype(np.int64)) != 15 * 60 * 1_000_000_000):
            raise ValueError(f"non-contiguous model time axis in {grid}")
        selected = times[
            (times >= np.datetime64(start.replace(tzinfo=None), "ns"))
            & (times <= np.datetime64(end.replace(tzinfo=None), "ns"))
        ]
        state.update(
            {
                "source_first_time": str(times[0]),
                "source_last_time": str(times[-1]),
                "registered_window_steps": int(selected.size),
                "registered_first_time": str(selected[0]),
                "registered_last_time": str(selected[-1]),
            }
        )
        rendered_grids[grid] = state
    return {
        "schema_version": 1,
        "status": "pass",
        "file_count": len(downloads),
        "maximum_timestamp_adjustment_seconds": maximum_error,
        "grids": rendered_grids,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "data/manifests/helgoland_reproduction_inputs.json",
    )
    parser.add_argument("--input-dir", type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = json.loads(args.manifest.read_text())
    result = audit(manifest, args.input_dir)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        output_root = args.input_dir or Path(
            next(row for row in manifest["inputs"] if row["id"] == "bsh-hbmnoku")[
                "remote_directory"
            ]
        )
        (output_root / "structural_audit.json").write_text(rendered)
    else:
        args.output.write_text(rendered)
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
