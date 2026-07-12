"""Compute Route-A low-frequency coverage requirements from P1-E006 signals."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import run_p1_evidence_bounded_atlas as atlas  # noqa: E402

from oceangravity.evaluation import canonicalize_report_floats  # noqa: E402
from oceangravity.instruments import load_noise_curves  # noqa: E402
from oceangravity.signal_processing import low_frequency_coverage_requirements  # noqa: E402


def _summaries(records: list[dict], thresholds: tuple[float, ...]) -> dict:
    summary = {}
    for process in sorted({row["process"] for row in records}):
        rows = [row for row in records if row["process"] == process]
        summary[process] = {"record_count": len(rows), "thresholds": {}}
        for threshold in thresholds:
            key = str(threshold)
            values = np.asarray(
                [
                    row["intrinsic_requirements"][key]["maximum_admissible_low_frequency_hz"]
                    for row in rows
                ]
            )
            summary[process]["thresholds"][key] = {
                "minimum_hz": float(np.min(values)),
                "median_hz": float(np.median(values)),
                "maximum_hz": float(np.max(values)),
            }
    return summary


def run(config: dict) -> dict:
    source_config = json.loads((ROOT / config["source_config"]).read_text())
    source_metrics = json.loads((ROOT / config["source_metrics"]).read_text())
    thresholds = tuple(map(float, config["required_energy_fractions"]))
    curves_by_id = load_noise_curves(ROOT / config["instrument_curve_manifest"])
    curves = [curves_by_id[curve_id] for curve_id in config["authorized_vertical_gravity_curves"]]
    records: list[dict] = []

    original_record = atlas._record

    def coverage_record(process, variant, distance_m, parameters, values, interval, _curves, _cfg):
        intrinsic = low_frequency_coverage_requirements(values, interval, thresholds)
        instruments = {}
        for curve in curves:
            requirements = low_frequency_coverage_requirements(
                values,
                interval,
                thresholds,
                maximum_frequency_hz=curve.frequencies_hz[-1],
            )
            instruments[curve.instrument_id] = {
                str(item.required_energy_fraction): {
                    **asdict(item),
                    "published_low_frequency_hz": curve.frequencies_hz[0],
                    "low_edge_gap_ratio": (
                        None
                        if item.maximum_admissible_low_frequency_hz is None
                        else curve.frequencies_hz[0] / item.maximum_admissible_low_frequency_hz
                    ),
                    "published_band_meets_coverage": (
                        item.maximum_admissible_low_frequency_hz is not None
                        and curve.frequencies_hz[0] <= item.maximum_admissible_low_frequency_hz
                    ),
                }
                for item in requirements
            }
        return {
            "process": process,
            "model_variant": variant,
            "distance_standoff_m": distance_m,
            "parameters": parameters,
            "sample_interval_s": interval,
            "sample_count": len(values),
            "nyquist_frequency_hz": 0.5 / interval,
            "intrinsic_requirements": {
                str(item.required_energy_fraction): asdict(item) for item in intrinsic
            },
            "instrument_band_requirements": instruments,
        }

    try:
        atlas._record = coverage_record
        for builder in (
            atlas._tide_records,
            atlas._storm_records,
            atlas._eddy_records,
            atlas._internal_wave_records,
            atlas._tsunami_records,
            atlas._landslide_records,
        ):
            records.extend(builder(source_config, curves))
    finally:
        atlas._record = original_record

    if len(records) != source_metrics["record_count"]:
        raise RuntimeError("reconstructed record count differs from P1-E006")
    process_counts = {
        process: sum(row["process"] == process for row in records)
        for process in sorted({row["process"] for row in records})
    }
    if process_counts != source_metrics["process_record_counts"]:
        raise RuntimeError("reconstructed process counts differ from P1-E006")

    canonical = json.dumps(config, sort_keys=True, separators=(",", ":"))
    result = {
        "schema_version": 1,
        "experiment_id": config["experiment_id"],
        "result_class": "spectral_coverage_requirement_not_detectability",
        "config_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
        "source_experiment_id": config["source_experiment_id"],
        "record_count": len(records),
        "process_record_counts": process_counts,
        "required_energy_fractions": thresholds,
        "process_summary": _summaries(records, thresholds),
        "records": records,
        "claim_boundary": config["claim_boundary"],
    }
    return canonicalize_report_floats(
        result, significant_digits=config["report_significant_digits"]
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(json.loads(args.config.read_text()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
