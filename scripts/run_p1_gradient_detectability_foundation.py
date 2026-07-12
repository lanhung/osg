"""Evaluate six engineering process gradients against traceable gradient anchors."""

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

from oceangravity.evaluation import evaluate_gradient_signal_against_curve  # noqa: E402
from oceangravity.instruments import load_noise_curves  # noqa: E402
from run_p1_foundation import build_process_signals  # noqa: E402


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
    gradient_curves = {
        name: curve for name, curve in curves.items() if curve.observable == "gravity_gradient"
    }
    excluded_curves = {
        name: f"observable {curve.observable!r} does not match gravity_gradient signal"
        for name, curve in curves.items()
        if curve.observable != "gravity_gradient"
    }
    matrix = {}
    for process_name, (signal, interval, _) in processes.items():
        gradient = signal.vertical_direct_gravity_gradient_s2
        if gradient is None:
            raise ValueError(f"process {process_name!r} does not provide a Tzz series")
        matrix[process_name] = {
            curve_name: asdict(
                evaluate_gradient_signal_against_curve(
                    gradient,
                    interval,
                    curve,
                    required_expected_snr=config["required_expected_snr"],
                    minimum_signal_energy_coverage=config[
                        "minimum_signal_energy_coverage"
                    ],
                )
            )
            for curve_name, curve in gradient_curves.items()
        }
    canonical_config = json.dumps(config, sort_keys=True, separators=(",", ":"))
    return {
        "schema_version": 1,
        "experiment_id": "P1-E003-gradient-detectability-foundation",
        "result_class": "engineering_reference_not_cited_physical_prior",
        "config_sha256": hashlib.sha256(canonical_config.encode()).hexdigest(),
        "excluded_instrument_curves": excluded_curves,
        "matrix": matrix,
    }


def main() -> int:
    args = parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    result = run(config)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
