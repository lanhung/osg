"""Generate the evidence-bounded Paper 1 primary-branch atlas."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from oceangravity.constants import (  # noqa: E402
    GRAVITATIONAL_CONSTANT,
    MEAN_EARTH_RADIUS,
    REFERENCE_SEAWATER_DENSITY,
    STANDARD_GRAVITY,
)
from oceangravity.evaluation import (  # noqa: E402
    canonicalize_report_floats,
    evaluate_gravity_signal_against_curve,
)
from oceangravity.instruments import load_noise_curves  # noqa: E402
from oceangravity.processes import (  # noqa: E402
    mass_conserving_submarine_landslide,
    oscillating_compensated_gaussian_dipole,
    regular_times,
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


def _spherical_radial_weights(
    x_edges_m: np.ndarray,
    y_edges_m: np.ndarray,
    station_x_m: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return radial gravity per surface density and local cell centres."""

    radius = MEAN_EARTH_RADIUS.value
    longitude_edges = x_edges_m / radius
    latitude_edges = y_edges_m / radius
    longitude = 0.5 * (longitude_edges[:-1] + longitude_edges[1:])
    sine_south = np.sin(latitude_edges[:-1])
    sine_north = np.sin(latitude_edges[1:])
    latitude = np.arcsin(0.5 * (sine_south + sine_north))
    lat, lon = np.meshgrid(latitude, longitude, indexing="ij")
    areas = radius**2 * (sine_north - sine_south)[:, None] * np.diff(longitude_edges)[None, :]
    source_x = radius * np.cos(lat) * np.cos(lon)
    source_y = radius * np.cos(lat) * np.sin(lon)
    source_z = radius * np.sin(lat)
    station_lon = station_x_m / radius
    observation = np.array([radius * math.cos(station_lon), radius * math.sin(station_lon), 0.0])
    radial = observation / radius
    delta_x = source_x - observation[0]
    delta_y = source_y - observation[1]
    delta_z = source_z - observation[2]
    distance_squared = delta_x**2 + delta_y**2 + delta_z**2
    radial_displacement = delta_x * radial[0] + delta_y * radial[1] + delta_z * radial[2]
    weights = (
        GRAVITATIONAL_CONSTANT.value
        * areas
        * radial_displacement
        / (distance_squared * np.sqrt(distance_squared))
    )
    x_centres = 0.5 * (x_edges_m[:-1] + x_edges_m[1:])
    y_centres = 0.5 * (y_edges_m[:-1] + y_edges_m[1:])
    return weights, x_centres, y_centres


def _spherical_gaussian_patch_response(
    *,
    center_y_m: float,
    station_x_m: float,
    scale_m: float,
    peak_surface_density_kg_m2: float,
    cutoff_sigma: float,
    cells_per_sigma: int,
    target_signed_mass_kg: float | None = None,
) -> tuple[float, float]:
    """Integrate one compact Gaussian surface patch on the spherical Earth."""

    cell_count = 2 * round(cutoff_sigma * cells_per_sigma)
    x_edges = np.linspace(-cutoff_sigma * scale_m, cutoff_sigma * scale_m, cell_count + 1)
    y_edges = np.linspace(
        center_y_m - cutoff_sigma * scale_m,
        center_y_m + cutoff_sigma * scale_m,
        cell_count + 1,
    )
    weights, x_centres, y_centres = _spherical_radial_weights(x_edges, y_edges, station_x_m)
    x, y = np.meshgrid(x_centres, y_centres, indexing="xy")
    density = peak_surface_density_kg_m2 * np.exp(
        -0.5 * (x**2 + (y - center_y_m) ** 2) / scale_m**2
    )
    radius = MEAN_EARTH_RADIUS.value
    latitude_edges = y_edges / radius
    areas = (
        radius**2
        * np.diff(x_edges / radius)[None, :]
        * (np.sin(latitude_edges[1:]) - np.sin(latitude_edges[:-1]))[:, None]
    )
    mass = float(np.sum(density * areas))
    if target_signed_mass_kg is not None:
        if mass == 0.0 or math.copysign(1.0, mass) != math.copysign(1.0, target_signed_mass_kg):
            raise ValueError("Gaussian patch cannot be normalized to the requested signed mass")
        density *= target_signed_mass_kg / mass
        mass = float(np.sum(density * areas))
    return float(np.sum(density * weights)), mass


def _spherical_disk_response(
    *, radius_m: float, station_standoff_m: float, surface_density_kg_m2: float
) -> float:
    cell_count = 48
    edges = np.linspace(-radius_m, radius_m, cell_count + 1)
    weights, x_centres, y_centres = _spherical_radial_weights(
        edges, edges, -(radius_m + station_standoff_m)
    )
    x, y = np.meshgrid(x_centres, y_centres, indexing="xy")
    density = np.where(x**2 + y**2 <= radius_m**2, surface_density_kg_m2, 0.0)
    return float(np.sum(density * weights))


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
        gravity_amplitude = _spherical_disk_response(
            radius_m=settings["disk_radius_m"],
            station_standoff_m=standoff,
            surface_density_kg_m2=density,
        )
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
    patch = config["spherical_patch"]
    station_offset = patch["cutoff_sigma"] * settings["horizontal_scale_m"]
    for standoff in config["distance_standoff_m"]:
        values = tuple(
            _spherical_gaussian_patch_response(
                center_y_m=settings["translation_speed_m_s"] * time,
                station_x_m=-(station_offset + standoff),
                scale_m=settings["horizontal_scale_m"],
                peak_surface_density_kg_m2=(
                    REFERENCE_SEAWATER_DENSITY.value * settings["peak_sea_level_anomaly_m"]
                ),
                cutoff_sigma=patch["cutoff_sigma"],
                cells_per_sigma=patch["cells_per_sigma"],
            )[0]
            for time in times
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
                values,
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
    patch = config["spherical_patch"]
    station_offset = patch["cutoff_sigma"] * scale
    for standoff in config["distance_standoff_m"]:
        for amplitude, length in zip(amplitudes, lengths, strict=True):
            duration = (length + 8.0 * scale) / speed
            times = regular_times(
                int(duration / interval) + 1,
                interval,
                start_time_s=-4 * scale / speed,
            )
            target_mass = (
                2.0
                * math.pi
                * REFERENCE_SEAWATER_DENSITY.value
                * amplitude
                * scale**2
                * (1.0 - math.exp(-0.5 * patch["cutoff_sigma"] ** 2))
            )
            values = []
            mass_residuals = []
            for time in times:
                crest, crest_mass = _spherical_gaussian_patch_response(
                    center_y_m=speed * time,
                    station_x_m=-(station_offset + standoff),
                    scale_m=scale,
                    peak_surface_density_kg_m2=(REFERENCE_SEAWATER_DENSITY.value * amplitude),
                    cutoff_sigma=patch["cutoff_sigma"],
                    cells_per_sigma=patch["cells_per_sigma"],
                    target_signed_mass_kg=target_mass,
                )
                trough, trough_mass = _spherical_gaussian_patch_response(
                    center_y_m=speed * time - length,
                    station_x_m=-(station_offset + standoff),
                    scale_m=scale,
                    peak_surface_density_kg_m2=(-REFERENCE_SEAWATER_DENSITY.value * amplitude),
                    cutoff_sigma=patch["cutoff_sigma"],
                    cells_per_sigma=patch["cells_per_sigma"],
                    target_signed_mass_kg=-target_mass,
                )
                values.append(math.fsum((crest, trough)))
                mass_residuals.append(math.fsum((crest_mass, trough_mass)))
            if max(abs(value) for value in mass_residuals) > target_mass * 1.0e-12:
                raise RuntimeError("tsunami signed surface mass does not close")
            records.append(
                _record(
                    "tsunami",
                    "dart_amplitude_mass_balanced_packet",
                    standoff,
                    {"deep_ocean_amplitude_m": amplitude, "source_length_m": length},
                    tuple(values),
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
