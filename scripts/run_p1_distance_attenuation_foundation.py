"""Evaluate engineering peak gravity and Tzz over explicit vertical standoffs."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from run_p1_foundation import build_process_signals  # noqa: E402


def _configuration_at_distance(base: dict, distance_m: float) -> dict:
    config = copy.deepcopy(base)
    config["tide"]["observation_z_m"] = config["tide"]["disk_z_m"] + distance_m
    config["storm_surge"]["observation_z_m"] = config["storm_surge"]["disk_z_m"] + distance_m
    config["eddy"]["observation_xyz_m"] = [
        0.0,
        0.0,
        config["eddy"]["anomaly_z_m"] + distance_m,
    ]
    internal_center = config["internal_wave"]["dipole_center_xyz_m"]
    config["internal_wave"]["observation_xyz_m"] = [
        internal_center[0],
        internal_center[1],
        internal_center[2] + distance_m,
    ]
    config["tsunami"]["observation_xyz_m"] = [
        0.0,
        0.0,
        config["tsunami"]["wave_plane_z_m"] + distance_m,
    ]
    source = config["landslide"]["solid_source_xyz_m"]
    destination = config["landslide"]["solid_destination_xyz_m"]
    midpoint = [0.5 * (left + right) for left, right in zip(source, destination, strict=True)]
    config["landslide"]["observation_xyz_m"] = [
        midpoint[0],
        midpoint[1],
        midpoint[2] + distance_m,
    ]
    return config


def run(config: dict) -> dict:
    base_path = ROOT / config["foundation_config"]
    base = json.loads(base_path.read_text(encoding="utf-8"))
    raw_distances = config["vertical_standoff_distances_m"]
    distances = tuple(float(value) for value in raw_distances)
    if not distances or not all(math.isfinite(value) and value > 0.0 for value in distances):
        raise ValueError("vertical standoff distances must be finite and positive")
    if any(distances[index + 1] <= distances[index] for index in range(len(distances) - 1)):
        raise ValueError("vertical standoff distances must be strictly increasing")

    process_records: dict[str, list[dict[str, float]]] = {}
    for distance in distances:
        built = build_process_signals(_configuration_at_distance(base, distance))
        for process_name, (signal, _, _) in built.items():
            gradient = signal.peak_absolute_gravity_gradient_s2
            if gradient is None:
                raise ValueError(f"process {process_name!r} lacks Tzz")
            process_records.setdefault(process_name, []).append(
                {
                    "vertical_standoff_m": distance,
                    "peak_absolute_direct_gravity_m_s2": signal.peak_absolute_gravity_m_s2,
                    "peak_absolute_direct_Tzz_s2": gradient,
                }
            )
    canonical_config = json.dumps(config, sort_keys=True, separators=(",", ":"))
    return {
        "schema_version": 1,
        "experiment_id": "P1-E004-distance-attenuation-foundation",
        "result_class": "engineering_reference_not_cited_physical_prior",
        "config_sha256": hashlib.sha256(canonical_config.encode()).hexdigest(),
        "distance_definition": {
            "tide_storm_eddy_tsunami": "vertical distance above load/reference plane",
            "internal_wave": "vertical distance above dipole centre",
            "landslide": "vertical distance above source-destination midpoint",
        },
        "processes": process_records,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run(json.loads(args.config.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
