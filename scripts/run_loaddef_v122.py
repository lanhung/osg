"""Run an externally stored, checksummed LoadDef v1.2.2 source tree under MPI."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import sys
from pathlib import Path
from typing import Any


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_inputs(config: dict[str, Any], source_root: Path, archive: Path) -> None:
    if config.get("schema_version") != 1:
        raise ValueError("unsupported LoadDef run-config schema")
    source = config["source"]
    if source.get("version") != "1.2.2":
        raise ValueError("this runner is restricted to LoadDef v1.2.2")
    checks = (
        (archive, source["archive_sha256"], "source archive"),
        (source_root / "LICENSE", source["license_sha256"], "license"),
        (
            source_root / config["planet_model"]["path"],
            config["planet_model"]["sha256"],
            "planet model",
        ),
    )
    for path, expected, label in checks:
        if not path.is_file():
            raise ValueError(f"{label} is missing: {path}")
        if _sha256(path) != expected:
            raise ValueError(f"{label} SHA-256 mismatch")
    production = config["production"]
    if production["startn"] != 0 or production["stopn"] < production["startn"]:
        raise ValueError("production Love-number degrees must begin at zero and increase")
    theta = tuple(float(value) for value in config["green_functions"]["theta"])
    if not theta or not all(math.isfinite(value) and 0.0 < value <= 180.0 for value in theta):
        raise ValueError("Green-function angles must lie in (0, 180] degrees")
    if any(right <= left for left, right in itertools.pairwise(theta)):
        raise ValueError("Green-function angles must be strictly increasing")


def _love_number_kwargs(section: dict[str, Any]) -> dict[str, Any]:
    mapping = {
        "startn": "startn",
        "stopn": "stopn",
        "period_hours": "period_hours",
        "r_min": "r_min",
        "inf_tol": "inf_tol",
        "rel_tol": "rel_tol",
        "abs_tol": "abs_tol",
        "backend": "backend",
        "nstps": "nstps",
        "gravitational_constant_m3_kg_s2": "G",
        "kx": "kx",
        "num_soln": "num_soln",
        "interp_emod": "interp_emod",
        "nongrav": "nongrav",
        "file_out": "file_out",
    }
    return {target: section[source] for source, target in mapping.items() if source in section}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--stage", choices=("smoke", "production", "greens"), required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    source_root = args.source_root.resolve()
    validate_inputs(config, source_root, args.archive.resolve())
    sys.path.insert(0, str(source_root))
    os.chdir(source_root / "working")

    from mpi4py import MPI

    rank = MPI.COMM_WORLD.Get_rank()
    size = MPI.COMM_WORLD.Get_size()
    planet_model = source_root / config["planet_model"]["path"]

    if args.stage in {"smoke", "production"}:
        from LOADGF.LN import compute_love_numbers

        if rank == 0:
            for name in ("LLN", "PLN", "STR", "SHR"):
                (source_root / "output/Love_Numbers" / name).mkdir(parents=True, exist_ok=True)
        MPI.COMM_WORLD.Barrier()
        section = config[args.stage]
        kwargs = _love_number_kwargs(section)
        compute_love_numbers.main(str(planet_model), rank, MPI.COMM_WORLD, size, **kwargs)
    else:
        from LOADGF.GF import compute_greens_functions

        if rank == 0:
            (source_root / "output/Greens_Functions").mkdir(parents=True, exist_ok=True)
        MPI.COMM_WORLD.Barrier()
        section = config["green_functions"]
        love_file = source_root / "output/Love_Numbers/LLN/lln_PREM.txt"
        compute_greens_functions.main(
            str(love_file),
            rank,
            MPI.COMM_WORLD,
            size,
            grn_out=section["output_name"],
            theta=section["theta"],
            a=section["earth_radius_m"],
            disk_factor=section["disk_factor"],
            angdist=section["disk_factor_start_deg"],
            disk_size=section["disk_radius_deg"],
            apply_taper=section["apply_taper"],
            max_theta=section["max_asymptotic_theta_deg"],
        )
    MPI.COMM_WORLD.Barrier()
    if rank == 0:
        print(json.dumps({"stage": args.stage, "mpi_ranks": size, "status": "completed"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
