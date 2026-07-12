"""Measure dependency-free spherical-load kernel time and Python peak memory."""

from __future__ import annotations

import argparse
import gc
import json
import math
import platform
import sys
import time
import tracemalloc
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from oceangravity.loading import surface_load_gravity_spherical  # noqa: E402


def _uniform_edges(start: float, stop: float, cells: int) -> list[float]:
    return [start + (stop - start) * index / cells for index in range(cells + 1)]


def benchmark_grid(
    latitude_cells: int,
    longitude_cells: int,
    chunk_sizes: tuple[int | None, ...],
) -> dict:
    if latitude_cells <= 0 or longitude_cells <= 0:
        raise ValueError("grid dimensions must be positive")
    density = [
        [1_025.0 * math.sin((row + 0.5) * math.pi / latitude_cells)] * longitude_cells
        for row in range(latitude_cells)
    ]
    latitude_edges = _uniform_edges(-60.0, 60.0, latitude_cells)
    longitude_edges = _uniform_edges(100.0, 160.0, longitude_cells)
    cases = []
    reference = None
    for chunk_size in chunk_sizes:
        gc.collect()
        tracemalloc.start()
        start = time.perf_counter()
        result = surface_load_gravity_spherical(
            density,
            latitude_edges,
            longitude_edges,
            20.0,
            120.0,
            100_000.0,
            chunk_size_cells=chunk_size,
        )
        elapsed = time.perf_counter() - start
        _, peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        if reference is None:
            reference = result.gravity_ecef_m_s2
        difference = max(
            abs(actual - expected)
            for actual, expected in zip(result.gravity_ecef_m_s2, reference, strict=True)
        )
        scale = max(max(abs(value) for value in reference), 1e-300)
        cases.append(
            {
                "chunk_size_cells": chunk_size,
                "elapsed_seconds": elapsed,
                "integrator_peak_traced_bytes": peak_bytes,
                "included_cells": result.included_cells,
                "maximum_relative_gravity_difference_from_unchunked": difference / scale,
            }
        )
    return {
        "schema_version": 1,
        "benchmark_id": "P1-WU31-spherical-load-scaling",
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "grid": {
            "latitude_cells": latitude_cells,
            "longitude_cells": longitude_cells,
            "total_cells": latitude_cells * longitude_cells,
        },
        "measurement_scope": "kernel wall time and tracemalloc Python allocation peak; input allocation and I/O excluded",
        "cases": cases,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--latitude-cells", type=int, default=90)
    parser.add_argument("--longitude-cells", type=int, default=180)
    parser.add_argument("--chunk-sizes", type=int, nargs="*", default=[256, 4096])
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = benchmark_grid(
        args.latitude_cells,
        args.longitude_cells,
        (None, *args.chunk_sizes),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
