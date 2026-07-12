"""Evaluate six engineering process fixtures against traceable gravity-noise anchors."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from run_p1_foundation import build_process_signals  # noqa: E402

from oceangravity.evaluation import (  # noqa: E402
    canonicalize_report_floats,
    evaluate_gravity_signal_against_curve,
)
from oceangravity.instruments import load_noise_curves  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def run(config: dict) -> dict:
    foundation_path = ROOT / config["foundation_config"]
    curve_path = ROOT / config["instrument_curve_manifest"]
    foundation_config = json.loads(foundation_path.read_text(encoding="utf-8"))
    processes = build_process_signals(foundation_config)
    curves = load_noise_curves(curve_path)
    gravity_curves = {
        name: curve for name, curve in curves.items() if curve.observable == "vertical_gravity"
    }
    excluded_curves = {
        name: f"observable {curve.observable!r} does not match vertical_gravity signal"
        for name, curve in curves.items()
        if curve.observable != "vertical_gravity"
    }
    matrix = {}
    for process_name, (signal, interval, _) in processes.items():
        matrix[process_name] = {
            curve_name: asdict(
                evaluate_gravity_signal_against_curve(
                    signal.vertical_direct_gravity_m_s2,
                    interval,
                    curve,
                    required_expected_snr=config["required_expected_snr"],
                    minimum_signal_energy_coverage=config["minimum_signal_energy_coverage"],
                    numerical_energy_coverage_floor=config["numerical_energy_coverage_floor"],
                )
            )
            for curve_name, curve in gravity_curves.items()
        }
    canonical_config = json.dumps(config, sort_keys=True, separators=(",", ":"))
    result = {
        "schema_version": 1,
        "experiment_id": "P1-E002-detectability-foundation",
        "result_class": "engineering_reference_not_cited_physical_prior",
        "config_sha256": hashlib.sha256(canonical_config.encode()).hexdigest(),
        "excluded_instrument_curves": excluded_curves,
        "matrix": matrix,
    }
    return canonicalize_report_floats(
        result,
        significant_digits=config["report_significant_digits"],
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
