"""Time-varying sea-level grids converted to auditable direct gravity signals."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from oceangravity.constants import REFERENCE_SEAWATER_DENSITY
from oceangravity.loading import (
    sea_level_to_surface_density,
    surface_load_gravity_spherical,
    surface_load_gravity_wgs84,
)

from .common import ScalarGravitySignal


@dataclass(frozen=True, slots=True)
class GriddedSeaLevelSignalResult:
    signal: ScalarGravitySignal
    included_mass_kg: tuple[float, ...]
    included_area_m2: tuple[float, ...]
    geometry: str


def gridded_sea_level_direct_gravity_signal(
    times_s: Sequence[float],
    sea_level_anomaly_m: Sequence[Sequence[Sequence[float | None]]],
    latitude_edges_deg: Sequence[float],
    longitude_edges_deg_unwrapped: Sequence[float],
    observation_latitude_deg: float,
    observation_longitude_deg: float,
    observation_height_m: float,
    *,
    geometry: str = "wgs84",
    water_density_kg_m3: float = REFERENCE_SEAWATER_DENSITY.value,
    water_mask: Sequence[Sequence[bool]] | None = None,
    cell_load_fraction: Sequence[Sequence[float]] | None = None,
    missing_policy: str = "error",
    load_height_m: float = 0.0,
    spherical_chunk_size_cells: int | None = 4096,
) -> GriddedSeaLevelSignalResult:
    """Compute direct local-up gravity for each sea-level grid without interpolation."""

    times = tuple(float(value) for value in times_s)
    if len(times) != len(sea_level_anomaly_m) or not times:
        raise ValueError("times and sea-level grids must have equal nonzero length")
    if not all(math.isfinite(value) for value in times):
        raise ValueError("times must be finite")
    if any(times[index + 1] <= times[index] for index in range(len(times) - 1)):
        raise ValueError("times must be strictly increasing")
    if geometry not in {"sphere", "wgs84"}:
        raise ValueError("geometry must be 'sphere' or 'wgs84'")

    gravity = []
    masses = []
    areas = []
    for grid in sea_level_anomaly_m:
        density_grid = sea_level_to_surface_density(grid, water_density_kg_m3)
        common = {
            "water_mask": water_mask,
            "cell_load_fraction": cell_load_fraction,
            "missing_policy": missing_policy,
        }
        if geometry == "sphere":
            result = surface_load_gravity_spherical(
                density_grid,
                latitude_edges_deg,
                longitude_edges_deg_unwrapped,
                observation_latitude_deg,
                observation_longitude_deg,
                observation_height_m,
                chunk_size_cells=spherical_chunk_size_cells,
                **common,
            )
            vertical = result.radial_gravity_m_s2
        else:
            result = surface_load_gravity_wgs84(
                density_grid,
                latitude_edges_deg,
                longitude_edges_deg_unwrapped,
                observation_latitude_deg,
                observation_longitude_deg,
                observation_height_m,
                load_height_m=load_height_m,
                **common,
            )
            vertical = result.geodetic_up_gravity_m_s2
        gravity.append(vertical)
        masses.append(result.included_mass_kg)
        areas.append(result.included_area_m2)

    signal = ScalarGravitySignal(
        process_id="gridded_sea_level_direct_gravity",
        times_s=times,
        source_amplitude=tuple(masses),
        source_amplitude_unit="kg signed included sea-level load mass",
        vertical_direct_gravity_m_s2=tuple(gravity),
        model_scope=f"direct attraction of gridded sea-level anomaly on {geometry}; no elastic response",
    )
    return GriddedSeaLevelSignalResult(
        signal=signal,
        included_mass_kg=tuple(masses),
        included_area_m2=tuple(areas),
        geometry=geometry,
    )
