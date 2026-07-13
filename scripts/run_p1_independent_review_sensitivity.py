"""Run the preregistered Paper 1 independent-review robustness audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import run_p1_evidence_bounded_atlas as atlas  # noqa: E402

from oceangravity.evaluation import (  # noqa: E402
    canonicalize_report_floats,
    evaluate_gravity_signal_against_curve,
)
from oceangravity.instruments import load_noise_curves  # noqa: E402
from oceangravity.signal_processing import (  # noqa: E402
    low_frequency_coverage_requirements,
    one_sided_spectrum,
)


def _parseval_requirements(
    values,
    interval: float,
    thresholds: tuple[float, ...],
    *,
    window: str,
) -> dict[str, float]:
    spectrum = one_sided_spectrum(values, interval, detrend="constant", window=window)
    frequencies = np.asarray(spectrum.frequencies_hz[1:])
    energies = np.asarray(spectrum.power_spectral_density[1:]) * spectrum.frequency_spacing_hz
    if frequencies.size < 2 or float(energies.sum()) <= 0.0:
        raise ValueError("positive-frequency energy must span at least two bins")
    suffix_fraction = np.cumsum(energies[::-1])[::-1] / energies.sum()
    requirements = {}
    for threshold in thresholds:
        allowed = np.flatnonzero(suffix_fraction >= threshold)
        if allowed.size == 0:
            raise RuntimeError("full positive-frequency band must meet every threshold")
        requirements[str(threshold)] = float(frequencies[allowed[-1]])
    return requirements


def _registered_requirements(values, interval: float, thresholds: tuple[float, ...]) -> dict:
    return {
        str(item.required_energy_fraction): item.maximum_admissible_low_frequency_hz
        for item in low_frequency_coverage_requirements(values, interval, thresholds)
    }


def _summary(records: list[dict], thresholds: tuple[float, ...], methods: tuple[str, ...]) -> dict:
    output = {}
    processes = sorted({record["process"] for record in records})
    for process in processes:
        rows = [record for record in records if record["process"] == process]
        output[process] = {"record_count": len(rows), "methods": {}}
        for method in methods:
            output[process]["methods"][method] = {}
            for threshold in thresholds:
                values = np.asarray([row["requirements"][method][str(threshold)] for row in rows])
                output[process]["methods"][method][str(threshold)] = {
                    "minimum_hz": float(values.min()),
                    "median_hz": float(np.median(values)),
                    "maximum_hz": float(values.max()),
                }
    return output


def run(config: dict) -> dict:
    source_config = json.loads((ROOT / config["source_config"]).read_text())
    source_metrics = json.loads((ROOT / config["source_metrics"]).read_text())
    source_frequency = json.loads((ROOT / config["source_frequency_metrics"]).read_text())
    thresholds = tuple(map(float, config["required_energy_fractions"]))
    curves_by_id = load_noise_curves(ROOT / config["instrument_curve_manifest"])
    curves = [curves_by_id[curve_id] for curve_id in config["authorized_vertical_gravity_curves"]]
    records: list[dict] = []

    original_record = atlas._record

    def review_record(process, variant, distance_m, parameters, values, interval, _curves, _cfg):
        requirements = {
            "registered_rectangular_trapezoid": _registered_requirements(
                values, interval, thresholds
            ),
            "rectangular_parseval_bins": _parseval_requirements(
                values, interval, thresholds, window="rectangular"
            ),
            "hann_parseval_bins": _parseval_requirements(
                values, interval, thresholds, window="hann-periodic"
            ),
        }
        statuses = {
            curve.instrument_id: evaluate_gravity_signal_against_curve(
                values,
                interval,
                curve,
                required_expected_snr=config["required_expected_snr"],
                minimum_signal_energy_coverage=config["minimum_signal_energy_coverage"],
            ).status
            for curve in curves
        }
        return {"process": process, "requirements": requirements, "statuses": statuses}

    try:
        atlas._record = review_record
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
    methods = tuple(item["id"] for item in config["spectral_conventions"])
    summary = _summary(records, thresholds, methods)
    status_summary: dict[str, dict[str, dict[str, int]]] = defaultdict(dict)
    for process in sorted(summary):
        process_rows = [record for record in records if record["process"] == process]
        for curve in curves:
            status_summary[process][curve.instrument_id] = dict(
                sorted(
                    Counter(row["statuses"][curve.instrument_id] for row in process_rows).items()
                )
            )

    registered_matches = {}
    for process, process_summary in summary.items():
        current = process_summary["methods"]["registered_rectangular_trapezoid"]
        frozen = source_frequency["process_summary"][process]["thresholds"]
        registered_matches[process] = all(
            math.isclose(current[str(threshold)]["median_hz"], frozen[str(threshold)]["median_hz"])
            for threshold in thresholds
        )

    lowest_edge = min(curve.frequencies_hz[0] for curve in curves)
    robustness = {
        process: {
            method: summary[process]["methods"][method]["0.9"]["median_hz"] < lowest_edge
            for method in methods
        }
        for process in summary
    }
    canonical = json.dumps(config, sort_keys=True, separators=(",", ":"))
    return canonicalize_report_floats(
        {
            "schema_version": 1,
            "experiment_id": config["experiment_id"],
            "result_class": "independent_review_robustness_not_detectability",
            "config_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
            "record_count": len(records),
            "reviewed_instrument_lowest_edge_hz": lowest_edge,
            "reviewed_instrument_bands_hz": {
                curve.instrument_id: [curve.frequencies_hz[0], curve.frequencies_hz[-1]]
                for curve in curves
            },
            "process_summary": summary,
            "reviewed_curve_status_summary": status_summary,
            "registered_e008_median_requirements_reproduced": registered_matches,
            "median_90pct_requirement_below_lowest_reviewed_edge": robustness,
            "all_robustness_checks_pass": all(
                value for process in robustness.values() for value in process.values()
            ),
            "claim_boundary": config["claim_boundary"],
        },
        significant_digits=config["report_significant_digits"],
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
