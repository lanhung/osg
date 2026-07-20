"""Run the preregistered Paper 1 temporal and spectral convergence audit."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import run_p1_evidence_bounded_atlas as atlas  # noqa: E402

from oceangravity.evaluation import (  # noqa: E402
    audit_curve_frequency_support,
    boundary_aware_spectral_energy,
    canonicalize_report_floats,
)
from oceangravity.instruments import load_noise_curves  # noqa: E402

BUILDERS = {
    "tide": atlas._tide_records,
    "storm_surge": atlas._storm_records,
    "mesoscale_eddy": atlas._eddy_records,
    "internal_wave": atlas._internal_wave_records,
    "tsunami": atlas._tsunami_records,
    "submarine_landslide": atlas._landslide_records,
}


def _dense_spectrum(values, interval: float, padding_factor: int) -> tuple[np.ndarray, np.ndarray]:
    samples = np.asarray(values, dtype=float)
    centred = samples - samples.mean()
    nfft = padding_factor * samples.size
    frequencies = np.fft.rfftfreq(nfft, d=interval)
    amplitudes = np.fft.rfft(centred, n=nfft) * interval
    return frequencies[1:], amplitudes[1:]


def _dense_requirements(
    values,
    interval: float,
    thresholds: tuple[float, ...],
    padding_factor: int,
) -> tuple[dict[str, float], np.ndarray, np.ndarray]:
    frequencies, amplitudes = _dense_spectrum(values, interval, padding_factor)
    powers = np.abs(amplitudes) ** 2
    segments = 0.5 * np.diff(frequencies) * (powers[:-1] + powers[1:])
    total = float(segments.sum())
    if frequencies.size < 2 or total <= 0.0:
        raise ValueError("positive-frequency energy must span at least two dense-grid points")
    suffix = np.concatenate((np.cumsum(segments[::-1])[::-1], np.array([0.0]))) / total
    output = {}
    for threshold in thresholds:
        eligible = np.flatnonzero(suffix >= threshold)
        if eligible.size == 0:
            raise RuntimeError("full positive-frequency grid must meet every threshold")
        output[str(threshold)] = float(frequencies[eligible[-1]])
    return output, frequencies, amplitudes


def _relative_change(left: float, right: float) -> float:
    return abs(right - left) / abs(right) if right != 0.0 else (0.0 if left == 0.0 else math.inf)


def _capture_records(builder, source_config: dict, curves) -> list[dict]:
    captured = []
    original = atlas._record

    def capture(process, variant, distance_m, parameters, values, interval, _curves, _config):
        record = {
            "process": process,
            "model_variant": variant,
            "distance_standoff_m": distance_m,
            "parameters": parameters,
            "sample_interval_s": float(interval),
            "sample_count": len(values),
            "values": tuple(float(value) for value in values),
        }
        captured.append(record)
        return record

    try:
        atlas._record = capture
        builder(source_config, curves)
    finally:
        atlas._record = original
    return captured


def _capture_all(source_config: dict, curves) -> list[dict]:
    records = []
    for builder in BUILDERS.values():
        records.extend(_capture_records(builder, source_config, curves))
    return records


def _summarize_dense(records: list[dict], thresholds, padding_factors) -> dict:
    summary = {}
    for process in sorted({row["process"] for row in records}):
        rows = [row for row in records if row["process"] == process]
        summary[process] = {"record_count": len(rows), "padding_factors": {}}
        for factor in padding_factors:
            summary[process]["padding_factors"][str(factor)] = {}
            for threshold in thresholds:
                values = np.asarray(
                    [row["dense_requirements"][str(factor)][str(threshold)] for row in rows]
                )
                summary[process]["padding_factors"][str(factor)][str(threshold)] = {
                    "minimum_hz": float(values.min()),
                    "median_hz": float(np.median(values)),
                    "maximum_hz": float(values.max()),
                }
    return summary


def _baseline_audit(source_config, source_metrics, curves, config) -> tuple[dict, list[dict]]:
    thresholds = tuple(map(float, config["required_energy_fractions"]))
    headline = str(float(config["headline_energy_fraction"]))
    padding_factors = tuple(config["dense_dtft"]["padding_factors"])
    compare_left, compare_right = map(str, config["dense_dtft"]["convergence_comparison"])
    records = _capture_all(source_config, curves)
    if len(records) != source_metrics["record_count"]:
        raise RuntimeError("reconstructed record count differs from P1-E006")
    native_status_counts: dict[str, dict[str, Counter]] = defaultdict(lambda: defaultdict(Counter))
    dense_pass_counts: dict[str, Counter] = defaultdict(Counter)
    convergence: dict[str, list[float]] = defaultdict(list)
    compact_records = []
    for row in records:
        dense = {}
        dense_spectra = {}
        for factor in padding_factors:
            requirements, frequencies, amplitudes = _dense_requirements(
                row["values"], row["sample_interval_s"], thresholds, factor
            )
            dense[str(factor)] = requirements
            dense_spectra[str(factor)] = (frequencies, amplitudes)
        convergence[row["process"]].append(
            _relative_change(dense[compare_left][headline], dense[compare_right][headline])
        )
        instrument_rows = {}
        frequencies, amplitudes = dense_spectra[str(max(padding_factors))]
        total_energy = boundary_aware_spectral_energy(
            frequencies, amplitudes, frequencies[0], frequencies[-1]
        )
        for curve in curves:
            support = audit_curve_frequency_support(
                row["sample_count"], row["sample_interval_s"], curve
            )
            native_status_counts[row["process"]][curve.instrument_id][support.status] += 1
            covered_energy = boundary_aware_spectral_energy(
                frequencies,
                amplitudes,
                curve.frequencies_hz[0],
                curve.frequencies_hz[-1],
            )
            fraction = covered_energy / total_energy if total_energy > 0.0 else 0.0
            if fraction >= float(config["headline_energy_fraction"]):
                dense_pass_counts[row["process"]][curve.instrument_id] += 1
            instrument_rows[curve.instrument_id] = {
                **asdict(support),
                "dense_boundary_aware_energy_coverage_fraction": fraction,
            }
        compact_records.append(
            {
                key: row[key]
                for key in (
                    "process",
                    "model_variant",
                    "distance_standoff_m",
                    "parameters",
                    "sample_interval_s",
                    "sample_count",
                )
            }
            | {
                "record_duration_s": row["sample_count"] * row["sample_interval_s"],
                "native_frequency_spacing_hz": 1.0
                / (row["sample_count"] * row["sample_interval_s"]),
                "source_nyquist_hz": (row["sample_count"] // 2)
                / (row["sample_count"] * row["sample_interval_s"]),
                "dense_requirements": dense,
                "headline_f_low_times_record_duration": dense[str(max(padding_factors))][headline]
                * row["sample_count"]
                * row["sample_interval_s"],
                "instrument_support": instrument_rows,
            }
        )
    tolerance = float(config["dense_dtft"]["relative_tolerance"])
    convergence_summary = {}
    for process, values in convergence.items():
        array = np.asarray(values)
        convergence_summary[process] = {
            "comparison_padding_factors": [int(compare_left), int(compare_right)],
            "median_relative_change": float(np.median(array)),
            "p95_relative_change": float(np.quantile(array, 0.95)),
            "maximum_relative_change": float(array.max()),
            "fraction_within_tolerance": float(np.mean(array <= tolerance)),
            "median_passes": float(np.median(array)) <= tolerance,
        }
    return (
        {
            "record_count": len(records),
            "process_summary": _summarize_dense(compact_records, thresholds, padding_factors),
            "grid_convergence": convergence_summary,
            "native_support_status_counts": {
                process: {
                    curve_id: dict(sorted(counts.items()))
                    for curve_id, counts in curve_rows.items()
                }
                for process, curve_rows in native_status_counts.items()
            },
            "dense_90pct_curve_coverage_pass_counts": {
                process: dict(counts) for process, counts in dense_pass_counts.items()
            },
        },
        compact_records,
    )


def _representative_config(source_config: dict, config: dict) -> dict:
    output = copy.deepcopy(source_config)
    design = config["representative_design"]
    output["distance_standoff_m"] = design["distance_standoff_m"]
    for process in ("tide", "internal_wave", "tsunami", "landslide_storegga"):
        output[process]["sample_count"] = design["parameter_sample_count"]
    return output


def _cadence_audit(source_config: dict, curves, config: dict) -> dict:
    base = _representative_config(source_config, config)
    multipliers = tuple(config["representative_design"]["cadence_multipliers"])
    headline = str(float(config["headline_energy_fraction"]))
    padding = max(config["dense_dtft"]["padding_factors"])
    base_rates = {
        "tide": ("samples_per_period", 16),
        "mesoscale_eddy": ("samples_per_characteristic_time", 8),
        "internal_wave": ("samples_per_period", 32),
        "tsunami": ("samples_per_scale_crossing", 6),
        "submarine_landslide": ("samples_per_transition", 32),
    }
    config_names = {
        "mesoscale_eddy": "eddy",
        "submarine_landslide": "landslide_storegga",
    }
    values_by_process: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for multiplier in multipliers:
        variant = copy.deepcopy(base)
        for process, (key, rate) in base_rates.items():
            variant[config_names.get(process, process)][key] = rate * multiplier
        for process, builder in BUILDERS.items():
            if process == "storm_surge":
                continue
            for row in _capture_records(builder, variant, curves):
                requirements, _frequencies, _amplitudes = _dense_requirements(
                    row["values"],
                    row["sample_interval_s"],
                    (float(headline),),
                    padding,
                )
                values_by_process[process][str(multiplier)].append(requirements[headline])
    left, right = map(str, config["representative_design"]["cadence_convergence_comparison"])
    tolerance = float(config["representative_design"]["relative_tolerance"])
    output = {}
    for process, by_multiplier in values_by_process.items():
        left_values = np.asarray(by_multiplier[left])
        right_values = np.asarray(by_multiplier[right])
        changes = np.abs(right_values - left_values) / np.abs(right_values)
        output[process] = {
            "record_count_per_multiplier": len(right_values),
            "median_f_low_hz_by_cadence_multiplier": {
                key: float(np.median(values)) for key, values in by_multiplier.items()
            },
            "comparison_multipliers": [int(left), int(right)],
            "median_relative_change": float(np.median(changes)),
            "maximum_relative_change": float(changes.max()),
            "fraction_within_tolerance": float(np.mean(changes <= tolerance)),
            "median_passes": float(np.median(changes)) <= tolerance,
        }
    return output


def _window_audit(source_config: dict, curves, config: dict) -> dict:
    base = _representative_config(source_config, config)
    design = config["record_window_design"]
    headline = float(config["headline_energy_fraction"])
    headline_key = str(headline)
    padding = max(config["dense_dtft"]["padding_factors"])
    variants = {
        "tide": (
            "observation_duration_s",
            design["tide_observation_duration_s"],
            {"endpoint_inclusive": design["tide_endpoint_inclusive"]},
        ),
        "mesoscale_eddy": (
            "window_half_width_characteristic_times",
            design["eddy_half_width_characteristic_times"],
            {},
        ),
        "internal_wave": (
            "window_periods",
            design["internal_wave_periods"],
            {"endpoint_inclusive": design["internal_wave_endpoint_inclusive"]},
        ),
        "tsunami": (
            "padding_scale_count",
            design["tsunami_padding_scale_count"],
            {},
        ),
        "submarine_landslide": (
            "padding_transition_durations",
            design["landslide_padding_transition_durations"],
            {},
        ),
    }
    config_names = {
        "mesoscale_eddy": "eddy",
        "submarine_landslide": "landslide_storegga",
    }
    output = {}
    for process, (key, values, extras) in variants.items():
        medians = []
        f_low_times_duration = []
        for value in values:
            variant = copy.deepcopy(base)
            section = variant[config_names.get(process, process)]
            if process == "tide":
                section[key] = [value, value]
                section["sample_count"] = 1
            else:
                section[key] = value
            section.update(extras)
            requirements = []
            products = []
            for row in _capture_records(BUILDERS[process], variant, curves):
                dense, _frequencies, _amplitudes = _dense_requirements(
                    row["values"], row["sample_interval_s"], (headline,), padding
                )
                requirement = dense[headline_key]
                requirements.append(requirement)
                products.append(requirement * row["sample_count"] * row["sample_interval_s"])
            medians.append(float(np.median(requirements)))
            f_low_times_duration.append(float(np.median(products)))
        relative_change = _relative_change(medians[-2], medians[-1])
        tolerance = float(design["largest_two_relative_tolerance"])
        output[process] = {
            "window_parameter": key,
            "window_values": values,
            "median_f_low_90_hz": medians,
            "median_f_low_times_record_duration": f_low_times_duration,
            "largest_two_relative_change": relative_change,
            "window_stable": relative_change <= tolerance,
        }

    document = json.loads((ROOT / source_config["helgoland_model_metrics"]).read_text())
    timestamps = [
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        for value in document["series"]["timestamps_utc"]
    ]
    storm_values = document["series"]["direct_attraction_detided_m_s2"]
    storm_rows = []
    for window in design["storm_windows_utc"]:
        start = datetime.fromisoformat(window["start"].replace("Z", "+00:00"))
        end = datetime.fromisoformat(window["end"].replace("Z", "+00:00"))
        values = [
            value
            for timestamp, value in zip(timestamps, storm_values, strict=True)
            if start <= timestamp < end
        ]
        dense, _frequencies, _amplitudes = _dense_requirements(
            values, document["time"]["cadence_s"], (headline,), padding
        )
        f_low = dense[headline_key]
        storm_rows.append(
            {
                **window,
                "sample_count": len(values),
                "f_low_90_hz": f_low,
                "f_low_times_record_duration": f_low * len(values) * document["time"]["cadence_s"],
            }
        )
    storm_change = _relative_change(storm_rows[-2]["f_low_90_hz"], storm_rows[-1]["f_low_90_hz"])
    output["storm_surge"] = {
        "window_parameter": "fixed_utc_window",
        "windows": storm_rows,
        "largest_two_relative_change": storm_change,
        "window_stable": storm_change <= float(design["largest_two_relative_tolerance"]),
        "cadence_note": "Hourly archive was not interpolated or upsampled.",
    }
    return output


def run(config: dict) -> dict:
    source_config = json.loads((ROOT / config["source_config"]).read_text())
    source_metrics = json.loads((ROOT / config["source_metrics"]).read_text())
    curve_map = load_noise_curves(ROOT / config["instrument_curve_manifest"])
    curves = [curve_map[curve_id] for curve_id in config["authorized_vertical_gravity_curves"]]
    baseline, records = _baseline_audit(source_config, source_metrics, curves, config)
    cadence = _cadence_audit(source_config, curves, config)
    windows = _window_audit(source_config, curves, config)
    dense_pass_total = sum(
        count
        for process in baseline["dense_90pct_curve_coverage_pass_counts"].values()
        for count in process.values()
    )
    grid_pass = all(row["median_passes"] for row in baseline["grid_convergence"].values())
    cadence_pass = all(row["median_passes"] for row in cadence.values())
    canonical = json.dumps(config, sort_keys=True, separators=(",", ":"))
    result = {
        "schema_version": 1,
        "experiment_id": config["experiment_id"],
        "result_class": "temporal_spectral_convergence_not_detectability",
        "config_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
        "source_experiment_id": config["source_experiment_id"],
        "baseline_audit": baseline,
        "cadence_audit": cadence,
        "window_audit": windows,
        "decision": {
            "dense_90pct_curve_coverage_pass_total": dense_pass_total,
            "zero_of_1446_classification_conclusion_stable": dense_pass_total == 0,
            "dense_grid_process_medians_converged": grid_pass,
            "representative_cadence_process_medians_converged": cadence_pass,
            "window_stable_processes": [
                process for process, row in windows.items() if row["window_stable"]
            ],
            "window_limited_processes": [
                process for process, row in windows.items() if not row["window_stable"]
            ],
            "update_exact_headline_requirements": not (
                grid_pass and cadence_pass and all(row["window_stable"] for row in windows.values())
            ),
        },
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
