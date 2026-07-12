"""Generate the evidence-bounded Paper 1 primary-branch atlas."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from oceangravity.constants import REFERENCE_SEAWATER_DENSITY, STANDARD_GRAVITY  # noqa: E402
from oceangravity.evaluation import (  # noqa: E402
    canonicalize_report_floats,
    evaluate_gravity_signal_against_curve,
)
from oceangravity.gravity import disk_gravity_numerical  # noqa: E402
from oceangravity.instruments import load_noise_curves  # noqa: E402
from oceangravity.processes import (  # noqa: E402
    mass_conserving_submarine_landslide,
    oscillating_compensated_gaussian_dipole,
    propagating_compensated_gaussian_tsunami,
    regular_times,
    translating_gaussian_surface_eddy,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def _linear_midpoints(bounds: list[float], count: int) -> tuple[float, ...]:
    lower, upper = map(float, bounds)
    return tuple(lower + (index + 0.5) / count * (upper - lower) for index in range(count))


def _log_midpoints(bounds: list[float], count: int) -> tuple[float, ...]:
    lower, upper = map(float, bounds)
    ratio = upper / lower
    return tuple(lower * ratio ** ((index + 0.5) / count) for index in range(count))


def _scaled(values: tuple[float, ...], scale: float) -> tuple[float, ...]:
    return tuple(scale * value for value in values)


def _classify(values, interval, curves, config) -> dict:
    return {
        curve.instrument_id: asdict(
            evaluate_gravity_signal_against_curve(
                values,
                interval,
                curve,
                required_expected_snr=config["required_expected_snr"],
                minimum_signal_energy_coverage=config["minimum_signal_energy_coverage"],
                numerical_energy_coverage_floor=config["numerical_energy_coverage_floor"],
            )
        )
        for curve in curves
    }


def _record(process, variant, distance_m, parameters, values, interval, curves, config):
    return {
        "process": process,
        "model_variant": variant,
        "distance_standoff_m": distance_m,
        "parameters": parameters,
        "sample_interval_s": interval,
        "sample_count": len(values),
        "peak_absolute_direct_gravity_m_s2": max(abs(value) for value in values),
        "detectability": _classify(values, interval, curves, config),
    }


def _tide_records(config, curves):
    settings = config["tide"]
    durations = _log_midpoints(settings["observation_duration_s"], settings["sample_count"])
    records = []
    density = REFERENCE_SEAWATER_DENSITY.value * settings["sea_level_normalization_m"]
    for standoff in config["distance_standoff_m"]:
        gravity_amplitude = disk_gravity_numerical(
            density,
            settings["disk_radius_m"],
            (0.0, 0.0, 0.0),
            (settings["disk_radius_m"] + standoff, 0.0, settings["observation_height_m"]),
            radial_cells=48,
            angular_cells=72,
        )[2]
        for duration in durations:
            interval = settings["period_s"] / 16.0
            count = max(33, int(duration / interval) + 1)
            times = regular_times(count, interval)
            values = tuple(
                gravity_amplitude * math.cos(2.0 * math.pi * time / settings["period_s"])
                for time in times
            )
            records.append(
                _record(
                    "tide",
                    "finite_disk_geometry_diagnostic_per_1m_ssh",
                    standoff,
                    {"observation_duration_s": duration},
                    values,
                    interval,
                    curves,
                    config,
                )
            )
    return records


def _storm_records(config, curves):
    document = json.loads((ROOT / config["helgoland_model_metrics"]).read_text())
    values = tuple(document["series"]["direct_attraction_detided_m_s2"])
    return [
        _record(
            "storm_surge",
            "bsh_hbmnoku_helgoland_direct_attraction",
            None,
            {"case_id": "helgoland-ntol-2022-voigt-2024"},
            values,
            document["time"]["cadence_s"],
            curves,
            config,
        )
    ]


def _eddy_records(config, curves):
    settings = config["eddy"]
    characteristic_time = settings["horizontal_scale_m"] / settings["translation_speed_m_s"]
    interval = characteristic_time / 8.0
    times = regular_times(65, interval, start_time_s=-4.0 * characteristic_time)
    records = []
    for standoff in config["distance_standoff_m"]:
        signal = translating_gaussian_surface_eddy(
            times,
            peak_sea_level_anomaly_m=settings["peak_sea_level_anomaly_m"],
            horizontal_scale_m=settings["horizontal_scale_m"],
            translation_speed_x_m_s=settings["translation_speed_m_s"],
            closest_approach_y_m=standoff,
            passage_time_s=0.0,
            anomaly_z_m=0.0,
            observation_xyz_m=(0.0, 0.0, settings["observation_height_m"]),
            radial_cells=settings["radial_cells"],
            angular_cells=settings["angular_cells"],
        )
        records.append(
            _record(
                "mesoscale_eddy",
                "catalogue_mean_gaussian_ssh",
                standoff,
                {
                    "peak_sea_level_anomaly_m": settings["peak_sea_level_anomaly_m"],
                    "horizontal_scale_m": settings["horizontal_scale_m"],
                    "translation_speed_m_s": settings["translation_speed_m_s"],
                },
                signal.vertical_direct_gravity_m_s2,
                interval,
                curves,
                config,
            )
        )
    return records


def _internal_wave_records(config, curves):
    settings = config["internal_wave"]
    densities = _linear_midpoints(settings["peak_density_anomaly_kg_m3"], settings["sample_count"])
    scales = _linear_midpoints(settings["horizontal_scale_m"], settings["sample_count"])
    interval = settings["period_s"] / 32.0
    times = regular_times(65, interval)
    records = []
    for standoff in config["distance_standoff_m"]:
        for density, scale in zip(densities, scales, strict=True):
            result = oscillating_compensated_gaussian_dipole(
                times,
                peak_density_anomaly_kg_m3=density,
                period_s=settings["period_s"],
                phase_rad=0.0,
                horizontal_scale_m=scale,
                vertical_scale_m=settings["vertical_scale_m"],
                lobe_separation_m=settings["lobe_separation_m"],
                dipole_center_xyz_m=(0.0, 0.0, -settings["center_depth_m"]),
                observation_xyz_m=(standoff, 0.0, 0.0),
                cells_per_axis=settings["cells_per_axis"],
            )
            records.append(
                _record(
                    "internal_wave",
                    "exactly_compensated_gaussian_dipole",
                    standoff,
                    {"peak_density_anomaly_kg_m3": density, "horizontal_scale_m": scale},
                    result.signal.vertical_direct_gravity_m_s2,
                    interval,
                    curves,
                    config,
                )
            )
    return records


def _tsunami_records(config, curves):
    settings = config["tsunami"]
    amplitudes = _linear_midpoints(settings["deep_ocean_amplitude_m"], settings["sample_count"])
    lengths = _linear_midpoints(settings["source_length_m"], settings["sample_count"])
    scale = settings["source_width_m"] / 2.0
    speed = math.sqrt(STANDARD_GRAVITY.value * settings["water_depth_m"])
    interval = scale / speed / 6.0
    records = []
    for standoff in config["distance_standoff_m"]:
        for amplitude, length in zip(amplitudes, lengths, strict=True):
            duration = (length + 8.0 * scale) / speed
            times = regular_times(
                int(duration / interval) + 1,
                interval,
                start_time_s=-4 * scale / speed,
            )
            result = propagating_compensated_gaussian_tsunami(
                times,
                crest_peak_sea_level_m=amplitude,
                horizontal_scale_m=scale,
                crest_trough_separation_m=length,
                water_depth_m=settings["water_depth_m"],
                crest_passage_time_s=0.0,
                wave_plane_z_m=0.0,
                observation_xyz_m=(0.0, standoff, settings["observation_height_m"]),
                radial_cells=settings["radial_cells"],
                angular_cells=settings["angular_cells"],
            )
            records.append(
                _record(
                    "tsunami",
                    "dart_amplitude_mass_balanced_packet",
                    standoff,
                    {"deep_ocean_amplitude_m": amplitude, "source_length_m": length},
                    result.signal.vertical_direct_gravity_m_s2,
                    interval,
                    curves,
                    config,
                )
            )
    return records


def _landslide_records(config, curves):
    settings = config["landslide_storegga"]
    volumes = _linear_midpoints(settings["slide_volume_m3"], settings["sample_count"])
    velocities = _linear_midpoints(settings["velocity_m_s"], settings["sample_count"])
    records = []
    for standoff in config["distance_standoff_m"]:
        for volume, velocity in zip(volumes, velocities, strict=True):
            duration = settings["runout_m"] / velocity
            interval = duration / 32.0
            times = regular_times(65, interval, start_time_s=-0.5 * duration)
            result = mass_conserving_submarine_landslide(
                times,
                solid_mass_kg=volume * settings["bulk_density_contrast_kg_m3"],
                solid_source_xyz_m=(-settings["runout_m"] / 2.0, 0.0, -settings["source_depth_m"]),
                solid_destination_xyz_m=(
                    settings["runout_m"] / 2.0,
                    0.0,
                    -settings["destination_depth_m"],
                ),
                transition_start_s=0.0,
                transition_duration_s=duration,
                observation_xyz_m=(0.0, standoff, 0.0),
            )
            records.append(
                _record(
                    "submarine_landslide",
                    "storegga_mass_conserving_point_pair",
                    standoff,
                    {"slide_volume_m3": volume, "velocity_m_s": velocity},
                    result.signal.vertical_direct_gravity_m_s2,
                    interval,
                    curves,
                    config,
                )
            )
    return records


def _status_summary(records, curve_ids):
    summary = {}
    for process in sorted({record["process"] for record in records}):
        process_records = [record for record in records if record["process"] == process]
        summary[process] = {}
        for curve_id in curve_ids:
            counts = {}
            for record in process_records:
                status = record["detectability"][curve_id]["status"]
                counts[status] = counts.get(status, 0) + 1
            summary[process][curve_id] = counts
    return summary


def run(config: dict) -> dict:
    curves_by_id = load_noise_curves(ROOT / config["instrument_curve_manifest"])
    curves = [curves_by_id[curve_id] for curve_id in config["authorized_vertical_gravity_curves"]]
    records = []
    for builder in (
        _tide_records,
        _storm_records,
        _eddy_records,
        _internal_wave_records,
        _tsunami_records,
        _landslide_records,
    ):
        records.extend(builder(config, curves))
    canonical_config = json.dumps(config, sort_keys=True, separators=(",", ":"))
    result = {
        "schema_version": 1,
        "experiment_id": config["experiment_id"],
        "result_class": "evidence_bounded_sensitivity_design_not_probability",
        "config_sha256": hashlib.sha256(canonical_config.encode()).hexdigest(),
        "record_count": len(records),
        "process_record_counts": {
            process: sum(record["process"] == process for record in records)
            for process in sorted({record["process"] for record in records})
        },
        "status_summary": _status_summary(records, config["authorized_vertical_gravity_curves"]),
        "records": records,
        "model_variant_disposition": {
            "mesoscale_eddy_catalogue_mean_quadratic_composite_ssh": "not_implemented_in_E006",
            "mesoscale_eddy_compensated_core_halo": (
                "validated_primitive_pending_positive_mass_normalization"
            ),
            "internal_wave_mode1_and_free_surface": "pending_stratified_mode_implementation",
            "tsunami_energy_normalized_branch": "pending_energy_to_packet_mapping",
            "landslide_mediterranean_and_storfjorden": (
                "amplitude_duration_pair_not_jointly_supported_by_current_evidence"
            ),
            "landslide_generated_water_wave": "pending_separate_component_branch",
        },
        "interpretation_limits": [
            "All parameter samples are sensitivity designs, not probability draws.",
            "Instrument results are conditional on literature anchors and their stated "
            "frequency ranges.",
            "Coverage-limited records are not assigned detectable or undetectable labels.",
            "Direct attraction is not silently summed with elastic or environmental components.",
        ],
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
