"""Close Paper 1 structural variants by implementation or explicit exclusion."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from oceangravity.evaluation import canonicalize_report_floats  # noqa: E402
from oceangravity.processes import gaussian_packet_amplitude_from_energy  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def _energy_branch(settings: dict) -> list[dict]:
    energy = float(settings["propagated_energy_j"])
    uncertainty = float(settings["relative_energy_uncertainty"])
    energies = (energy * (1.0 - uncertainty), energy, energy * (1.0 + uncertainty))
    records = []
    for separation in map(float, settings["crest_trough_separation_m"]):
        amplitudes = tuple(
            gaussian_packet_amplitude_from_energy(
                candidate,
                horizontal_scale_m=settings["horizontal_scale_m"],
                crest_trough_separation_m=separation,
                water_density_kg_m3=settings["water_density_kg_m3"],
            )
            for candidate in energies
        )
        records.append(
            {
                "crest_trough_separation_m": separation,
                "central_propagated_energy_j": energy,
                "relative_energy_uncertainty": uncertainty,
                "crest_peak_sea_level_m": {
                    "energy_minus_uncertainty": amplitudes[0],
                    "central": amplitudes[1],
                    "energy_plus_uncertainty": amplitudes[2],
                },
                "packet_net_surface_mass_kg": 0.0,
            }
        )
    return records


def run(config: dict) -> dict:
    manifest_path = ROOT / config["process_evidence_manifest"]
    evidence = json.loads(manifest_path.read_text(encoding="utf-8"))["processes"]
    tsunami_parameters = evidence["tsunami"]["production_joint_design"]["parameters"]
    registered_energy = tsunami_parameters["propagated_energy_J"]["value"]
    if not math.isclose(
        config["tsunami_energy_branch"]["propagated_energy_j"],
        registered_energy,
        rel_tol=0.0,
        abs_tol=0.0,
    ):
        raise ValueError("tsunami energy does not match the evidence manifest")

    decisions = config["variant_decisions"]
    allowed = {
        "implemented_evidence_bounded_sensitivity",
        "excluded_pending_design_resolution",
        "excluded_pending_physical_mapping",
        "excluded_insufficient_joint_evidence",
    }
    if len({row["variant_id"] for row in decisions}) != len(decisions):
        raise ValueError("variant IDs must be unique")
    if any(row["status"] not in allowed or not row["reason"].strip() for row in decisions):
        raise ValueError("every structural variant requires an allowed status and reason")
    unresolved = [row["variant_id"] for row in decisions if row["status"].startswith("pending")]
    canonical_config = json.dumps(config, sort_keys=True, separators=(",", ":"))
    result = {
        "schema_version": 1,
        "experiment_id": config["experiment_id"],
        "result_class": "structural_sensitivity_closure_not_probability",
        "config_sha256": hashlib.sha256(canonical_config.encode()).hexdigest(),
        "status": "pass" if not unresolved else "pending",
        "variant_decisions": decisions,
        "implemented_energy_branch": _energy_branch(config["tsunami_energy_branch"]),
        "interpretation": (
            "The energy-normalized tsunami branch is a discrete named-event sensitivity. "
            "Excluded branches are not assigned surrogate parameters, probability weights, "
            "or detectability labels."
        ),
    }
    return canonicalize_report_floats(
        result, significant_digits=config["report_significant_digits"]
    )


def main() -> int:
    args = parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    result = run(config)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
