"""Reproduce the open-data Helgoland BSH model branch on AutoDL.

The runner retains direct attraction, LoadDef CE combined elastic gravity, and
vertical displacement as separate series.  It performs an area-conservative
rectilinear remap to the published 1/8-degree grid.  The compact JSON output is
the registered artifact; bulk NetCDF inputs remain outside Git.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path

import numpy as np
import xarray as xr
from scipy import sparse

GRAVITATIONAL_CONSTANT_M3_KG_S2 = 6.67430e-11
WGS84_SEMI_MAJOR_AXIS_M = 6378137.0
WGS84_INVERSE_FLATTENING = 298.257223563


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def coordinate_edges(centres: np.ndarray) -> np.ndarray:
    """Infer monotone cell edges from regular or irregular cell centres."""

    values = np.asarray(centres, dtype=float)
    if values.ndim != 1 or values.size < 2 or not np.isfinite(values).all():
        raise ValueError("coordinate centres must be a finite one-dimensional array")
    if np.all(np.diff(values) < 0.0):
        values = values[::-1]
    if not np.all(np.diff(values) > 0.0):
        raise ValueError("coordinate centres must be strictly monotone")
    edges = np.empty(values.size + 1)
    edges[1:-1] = 0.5 * (values[:-1] + values[1:])
    edges[0] = values[0] - 0.5 * (values[1] - values[0])
    edges[-1] = values[-1] + 0.5 * (values[-1] - values[-2])
    return edges


def interval_overlap_matrix(
    target_edges: np.ndarray, source_edges: np.ndarray
) -> sparse.csr_matrix:
    """Return target-by-source interval overlaps in the coordinate's own units."""

    target = np.asarray(target_edges, dtype=float)
    source = np.asarray(source_edges, dtype=float)
    if not (np.all(np.diff(target) > 0.0) and np.all(np.diff(source) > 0.0)):
        raise ValueError("source and target edges must be strictly increasing")
    rows: list[int] = []
    columns: list[int] = []
    values: list[float] = []
    source_index = 0
    for target_index, (left, right) in enumerate(itertools.pairwise(target)):
        while source_index + 1 < source.size and source[source_index + 1] <= left:
            source_index += 1
        index = source_index
        while index + 1 < source.size and source[index] < right:
            overlap = min(right, source[index + 1]) - max(left, source[index])
            if overlap > 0.0:
                rows.append(target_index)
                columns.append(index)
                values.append(float(overlap))
            index += 1
    return sparse.csr_matrix(
        (values, (rows, columns)),
        shape=(target.size - 1, source.size - 1),
    )


def _ellipsoid_area_coordinate(latitude_deg: np.ndarray) -> np.ndarray:
    flattening = 1.0 / WGS84_INVERSE_FLATTENING
    eccentricity_squared = flattening * (2.0 - flattening)
    eccentricity = math.sqrt(eccentricity_squared)
    sine = np.sin(np.radians(latitude_deg))
    denominator = 1.0 - eccentricity_squared * sine**2
    integral = 0.5 * (sine / denominator + np.arctanh(eccentricity * sine) / eccentricity)
    return WGS84_SEMI_MAJOR_AXIS_M**2 * (1.0 - eccentricity_squared) * integral


def build_remap_operators(
    source_latitude_centres_deg: np.ndarray,
    source_longitude_centres_deg: np.ndarray,
    target_latitude_edges_deg: np.ndarray,
    target_longitude_edges_deg: np.ndarray,
) -> tuple[sparse.csr_matrix, sparse.csr_matrix, np.ndarray, np.ndarray]:
    """Build separable exact-area overlap operators for a WGS84 grid."""

    latitude_centres = np.asarray(source_latitude_centres_deg, dtype=float)
    reverse_latitude = np.all(np.diff(latitude_centres) < 0.0)
    latitude_edges = coordinate_edges(latitude_centres)
    longitude_edges = coordinate_edges(np.asarray(source_longitude_centres_deg, dtype=float))
    latitude_operator = interval_overlap_matrix(
        _ellipsoid_area_coordinate(target_latitude_edges_deg),
        _ellipsoid_area_coordinate(latitude_edges),
    )
    longitude_operator = interval_overlap_matrix(
        np.radians(target_longitude_edges_deg), np.radians(longitude_edges)
    )
    return latitude_operator, longitude_operator, latitude_edges, np.array([reverse_latitude])


def conservative_integrated_field(
    values: np.ndarray,
    latitude_operator: sparse.csr_matrix,
    longitude_operator: sparse.csr_matrix,
    *,
    reverse_latitude: bool,
) -> np.ndarray:
    """Integrate a cell-mean field over every target cell in field-unit m2."""

    field = np.asarray(values, dtype=float)
    if reverse_latitude:
        field = field[::-1, :]
    field = np.nan_to_num(field, nan=0.0)
    return np.asarray(latitude_operator @ field @ longitude_operator.T)


def _target_edges(bounds: list[float], spacing: float) -> np.ndarray:
    count = round((bounds[1] - bounds[0]) / spacing)
    if not math.isclose(bounds[0] + count * spacing, bounds[1], abs_tol=1e-10):
        raise ValueError("target-grid bounds must contain an integer number of cells")
    return np.linspace(bounds[0], bounds[1], count + 1)


def canonicalize_bsh_times(values: np.ndarray) -> np.ndarray:
    """Round decoded BSH timestamps to the nearest whole second."""

    times = np.asarray(values).astype("datetime64[ns]")
    rounded = (times + np.timedelta64(500, "ms")).astype("datetime64[s]")
    adjustment = np.abs(times - rounded.astype("datetime64[ns]"))
    if np.any(adjustment > np.timedelta64(500, "ms")):
        raise ValueError("BSH timestamp adjustment exceeds the registered 0.5 s bound")
    return rounded


def _load_green_table(
    path: Path, earth_radius_m: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    parsed_rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        tokens = line.split()
        if len(tokens) < 6:
            continue
        try:
            parsed_rows.append(tuple(float(tokens[index]) for index in (0, 1, 5)))
        except ValueError:
            continue
    rows = np.asarray(parsed_rows)
    if rows.ndim != 2 or rows.shape[0] < 2 or rows.shape[1] != 3:
        raise ValueError("LoadDef table must contain at least two numeric response rows")
    theta_rad = np.radians(rows[:, 0])
    displacement = rows[:, 1]
    elastic_gravity = rows[:, 2] / (1.0e18 * earth_radius_m * theta_rad)
    return theta_rad, elastic_gravity, displacement


def _angular_distance_rad(
    latitude_deg: np.ndarray,
    longitude_deg: np.ndarray,
    station_latitude_deg: float,
    station_longitude_deg: float,
) -> np.ndarray:
    latitude = np.radians(latitude_deg)
    longitude = np.radians(longitude_deg)
    station_latitude = math.radians(station_latitude_deg)
    station_longitude = math.radians(station_longitude_deg)
    cosine = np.sin(latitude) * math.sin(station_latitude) + np.cos(latitude) * math.cos(
        station_latitude
    ) * np.cos(longitude - station_longitude)
    return np.arccos(np.clip(cosine, -1.0, 1.0))


def _geodetic_ecef(latitude_deg: np.ndarray, longitude_deg: np.ndarray, height_m: float):
    flattening = 1.0 / WGS84_INVERSE_FLATTENING
    eccentricity_squared = flattening * (2.0 - flattening)
    latitude = np.radians(latitude_deg)
    longitude = np.radians(longitude_deg)
    prime_vertical = WGS84_SEMI_MAJOR_AXIS_M / np.sqrt(
        1.0 - eccentricity_squared * np.sin(latitude) ** 2
    )
    return (
        (prime_vertical + height_m) * np.cos(latitude) * np.cos(longitude),
        (prime_vertical + height_m) * np.cos(latitude) * np.sin(longitude),
        (prime_vertical * (1.0 - eccentricity_squared) + height_m) * np.sin(latitude),
    )


def _response_weights(config: dict, lat_edges: np.ndarray, lon_edges: np.ndarray):
    lat = 0.5 * (lat_edges[:-1] + lat_edges[1:])[:, None]
    lon = 0.5 * (lon_edges[:-1] + lon_edges[1:])[None, :]
    station = config["station"]
    theta = _angular_distance_rad(lat, lon, station["latitude_deg"], station["longitude_deg"])
    table_theta, table_elastic, table_displacement = _load_green_table(
        Path(config["loaddef_ce_green_function"]), config["earth_radius_m"]
    )
    if theta.min() < table_theta.min() or theta.max() > table_theta.max():
        raise ValueError("target cells fall outside the audited LoadDef angular-distance table")
    elastic = np.interp(theta, table_theta, table_elastic)
    displacement = np.interp(theta, table_theta, table_displacement)

    source = _geodetic_ecef(lat, lon, 0.0)
    observation = _geodetic_ecef(
        np.asarray(station["latitude_deg"]),
        np.asarray(station["longitude_deg"]),
        station["height_m"],
    )
    delta = tuple(source[index] - observation[index] for index in range(3))
    distance_squared = sum(component**2 for component in delta)
    scale = GRAVITATIONAL_CONSTANT_M3_KG_S2 / (distance_squared * np.sqrt(distance_squared))
    up = (
        math.cos(math.radians(station["latitude_deg"]))
        * math.cos(math.radians(station["longitude_deg"])),
        math.cos(math.radians(station["latitude_deg"]))
        * math.sin(math.radians(station["longitude_deg"])),
        math.sin(math.radians(station["latitude_deg"])),
    )
    direct = scale * sum(delta[index] * up[index] for index in range(3))
    return direct.ravel(), elastic.ravel(), displacement.ravel()


def _harmonic_residual(times: np.ndarray, values: np.ndarray, detiding: dict) -> np.ndarray:
    hours = (times - times[0]) / np.timedelta64(1, "h")
    columns = [np.ones(hours.size)]
    if detiding["include_linear_trend"]:
        columns.append((hours - hours.mean()) / 24.0)
    for cycles_per_day in detiding["constituents_cycles_per_solar_day"].values():
        phase = 2.0 * math.pi * cycles_per_day * hours / 24.0
        columns.extend((np.sin(phase), np.cos(phase)))
    design = np.column_stack(columns)
    fitted = design @ np.linalg.lstsq(design, values, rcond=None)[0]
    return values - fitted


def _summary(values: np.ndarray) -> dict[str, float]:
    return {
        "minimum": float(values.min()),
        "maximum": float(values.max()),
        "peak_to_peak": float(np.ptp(values)),
        "rms": float(np.sqrt(np.mean(values**2))),
    }


def run(config: dict) -> dict:
    input_root = Path(config["input_root"])
    files = {grid: sorted((input_root / grid).glob("*.nc")) for grid in ("fine", "coarse")}
    if len(files["fine"]) != 121 or len(files["coarse"]) != 121:
        raise ValueError("expected 121 fine and 121 coarse BSH cycle files")

    spacing = float(config["target_grid"]["spacing_deg"])
    target_lat_edges = _target_edges(config["target_grid"]["latitude_bounds_deg"], spacing)
    target_lon_edges = _target_edges(config["target_grid"]["longitude_bounds_deg"], spacing)
    operators = {}
    source_edges = {}
    for grid in ("fine", "coarse"):
        with xr.open_dataset(files[grid][0]) as dataset:
            lat_operator, lon_operator, lat_edges, reverse = build_remap_operators(
                dataset.lat.values, dataset.lon.values, target_lat_edges, target_lon_edges
            )
            operators[grid] = (lat_operator, lon_operator, bool(reverse[0]))
            source_edges[grid] = (lat_edges, coordinate_edges(dataset.lon.values))

    fine_lat_edges, fine_lon_edges = source_edges["fine"]
    fine_override = (
        (target_lat_edges[:-1, None] >= fine_lat_edges[0])
        & (target_lat_edges[1:, None] <= fine_lat_edges[-1])
        & (target_lon_edges[None, :-1] >= fine_lon_edges[0])
        & (target_lon_edges[None, 1:] <= fine_lon_edges[-1])
    )
    direct_weight, elastic_weight, displacement_weight = _response_weights(
        config, target_lat_edges, target_lon_edges
    )

    start = np.datetime64(config["analysis_window"]["start_utc"])
    end = np.datetime64(config["analysis_window"]["end_utc"])
    all_times: list[np.datetime64] = []
    direct_series: list[float] = []
    elastic_series: list[float] = []
    displacement_series: list[float] = []
    for fine_path, coarse_path in zip(files["fine"], files["coarse"], strict=True):
        with xr.open_dataset(fine_path) as fine_ds, xr.open_dataset(coarse_path) as coarse_ds:
            fine_times = canonicalize_bsh_times(fine_ds.time.values)
            coarse_times = canonicalize_bsh_times(coarse_ds.time.values)
            if not np.array_equal(fine_times, coarse_times):
                raise ValueError("fine and coarse files have mismatched timestamps")
            selected = np.flatnonzero(
                (fine_times >= start)
                & (fine_times <= end)
                & ((fine_times.astype("datetime64[m]").astype(int) % 60) == 0)
            )
            for index in selected:
                remapped = {}
                for grid, dataset in (("fine", fine_ds), ("coarse", coarse_ds)):
                    lat_operator, lon_operator, reverse = operators[grid]
                    remapped[grid] = conservative_integrated_field(
                        dataset.elev.isel(time=index).values,
                        lat_operator,
                        lon_operator,
                        reverse_latitude=reverse,
                    )
                integrated_ssh_m3 = np.where(fine_override, remapped["fine"], remapped["coarse"])
                mass_kg = config["water_density_kg_m3"] * integrated_ssh_m3.ravel()
                all_times.append(fine_times[index])
                direct_series.append(float(direct_weight @ mass_kg))
                elastic_series.append(float(elastic_weight @ mass_kg))
                displacement_series.append(float(displacement_weight @ mass_kg))

    times = np.asarray(all_times)
    if times.size != np.unique(times).size or not np.all(np.diff(times) == np.timedelta64(1, "h")):
        raise ValueError("registered BSH output must be unique and exactly hourly")
    direct = np.asarray(direct_series)
    elastic = np.asarray(elastic_series)
    displacement = np.asarray(displacement_series)
    detided = {
        "direct_attraction_m_s2": _harmonic_residual(times, direct, config["harmonic_detiding"]),
        "combined_elastic_gravity_m_s2": _harmonic_residual(
            times, elastic, config["harmonic_detiding"]
        ),
        "vertical_displacement_m": _harmonic_residual(
            times, displacement, config["harmonic_detiding"]
        ),
    }
    event_start = np.datetime64(config["event_window"]["start_utc"])
    event_end = np.datetime64(config["event_window"]["end_utc"])
    event = (times >= event_start) & (times <= event_end)
    target = config["published_model_target"]
    height = detided["vertical_displacement_m"]
    gravity = detided["combined_elastic_gravity_m_s2"]
    centered_height = height - height.mean()
    centered_gravity = gravity - gravity.mean()
    gravity_to_height_ratio = float(
        (centered_height @ centered_gravity) / (centered_height @ centered_height) * 1.0e6
    )
    ratio_fractional_error = abs(
        gravity_to_height_ratio - target["gravity_to_height_ratio_nm_s2_per_mm"]
    ) / abs(target["gravity_to_height_ratio_nm_s2_per_mm"])
    return {
        "schema_version": 1,
        "experiment_id": config["experiment_id"],
        "result_class": "published_case_model_reproduction_with_declared_detiding_difference",
        "config_sha256": hashlib.sha256(
            json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "time": {
            "sample_count": int(times.size),
            "first_utc": str(times[0]) + "Z",
            "last_utc": str(times[-1]) + "Z",
            "cadence_s": 3600,
        },
        "grid": {
            "spacing_deg": spacing,
            "shape": [target_lat_edges.size - 1, target_lon_edges.size - 1],
            "fine_override_cell_count": int(fine_override.sum()),
            "remap_conservation_semantics": "WGS84 exact-area intersection integral",
        },
        "components": {
            name: {
                "full_series_summary": _summary(values),
                "detided_series_summary": _summary(detided[name]),
                "event_summary": _summary(detided[name][event]),
            }
            for name, values in (
                ("direct_attraction_m_s2", direct),
                ("combined_elastic_gravity_m_s2", elastic),
                ("vertical_displacement_m", displacement),
            )
        },
        "series": {
            "timestamps_utc": [str(value) + "Z" for value in times],
            "direct_attraction_detided_m_s2": detided["direct_attraction_m_s2"].tolist(),
            "combined_elastic_gravity_detided_m_s2": detided[
                "combined_elastic_gravity_m_s2"
            ].tolist(),
            "vertical_displacement_detided_m": detided["vertical_displacement_m"].tolist(),
        },
        "published_model_target_comparison": {
            "gravity_to_height_ratio_nm_s2_per_mm": gravity_to_height_ratio,
            "published_gravity_to_height_ratio_nm_s2_per_mm": target[
                "gravity_to_height_ratio_nm_s2_per_mm"
            ],
            "fractional_error": ratio_fractional_error,
            "registered_fractional_tolerance": target["fractional_tolerance"],
            "status": "pass"
            if ratio_fractional_error <= target["fractional_tolerance"]
            else "quantified_discrepancy",
        },
        "published_observation_context": config["published_observation_context"],
        "limitations": [
            config["harmonic_detiding"]["scope_warning"],
            "LoadDef PREM/CE replaces the paper's SPOTL Gutenberg-Bullen response.",
            "Observation correlation and RMS reduction remain unclassified without "
            "authenticated iGrav Level 1 data.",
        ],
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
