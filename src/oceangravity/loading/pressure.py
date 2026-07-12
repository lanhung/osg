"""Pressure-to-load primitives for atmospheric and inverse-barometer models."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from oceangravity.constants import REFERENCE_SEAWATER_DENSITY, STANDARD_GRAVITY


Grid = Sequence[Sequence[float | None]]


@dataclass(frozen=True, slots=True)
class InverseBarometerResult:
    """Equilibrium sea-level response to pressure anomalies over an ocean domain."""

    sea_level_anomaly_m: tuple[tuple[float | None, ...], ...]
    ocean_mean_pressure_anomaly_pa: float
    included_area_m2: float
    net_surface_mass_anomaly_kg: float
    remove_ocean_mean: bool


def _rectangular_shape(grid: Sequence[Sequence[object]], name: str) -> tuple[int, int]:
    if not grid or not grid[0]:
        raise ValueError(f"{name} must be a non-empty rectangular grid")
    columns = len(grid[0])
    if any(len(row) != columns for row in grid):
        raise ValueError(f"{name} must be a non-empty rectangular grid")
    return len(grid), columns


def pressure_anomaly_to_column_surface_density(
    pressure_anomaly_pa: Grid,
    *,
    gravity_m_s2: float = STANDARD_GRAVITY.value,
) -> tuple[tuple[float | None, ...], ...]:
    """Convert surface-pressure anomaly to equivalent atmospheric column mass.

    This is the hydrostatic column identity ``sigma = delta_p / g``. It does not
    specify the vertical distribution needed for a production direct-attraction
    calculation.
    """

    _rectangular_shape(pressure_anomaly_pa, "pressure anomaly")
    gravity = float(gravity_m_s2)
    if not math.isfinite(gravity) or gravity <= 0.0:
        raise ValueError("gravity_m_s2 must be finite and positive")
    return tuple(
        tuple(
            None
            if value is None or not math.isfinite(float(value))
            else float(value) / gravity
            for value in row
        )
        for row in pressure_anomaly_pa
    )


def inverse_barometer_sea_level_anomaly(
    pressure_anomaly_pa: Grid,
    cell_area_m2: Sequence[Sequence[float]],
    *,
    ocean_mask: Sequence[Sequence[bool]] | None = None,
    cell_ocean_fraction: Sequence[Sequence[float]] | None = None,
    water_density_kg_m3: float = REFERENCE_SEAWATER_DENSITY.value,
    gravity_m_s2: float = STANDARD_GRAVITY.value,
    remove_ocean_mean: bool = True,
    missing_policy: str = "error",
) -> InverseBarometerResult:
    """Return the equilibrium inverse-barometer sea-level anomaly.

    With mean removal, ``eta = -(p - <p>_ocean)/(rho_w g)`` and the area-weighted
    water-mass anomaly closes to zero over the included domain. A regional subset
    should use this only when its pressure reference and open-boundary treatment
    justify that closure convention.
    """

    rows, columns = _rectangular_shape(pressure_anomaly_pa, "pressure anomaly")
    if _rectangular_shape(cell_area_m2, "cell area") != (rows, columns):
        raise ValueError("cell area shape must match pressure anomaly")
    if ocean_mask is not None and _rectangular_shape(ocean_mask, "ocean mask") != (
        rows,
        columns,
    ):
        raise ValueError("ocean mask shape must match pressure anomaly")
    if cell_ocean_fraction is not None and _rectangular_shape(
        cell_ocean_fraction, "cell ocean fraction"
    ) != (rows, columns):
        raise ValueError("cell ocean fraction shape must match pressure anomaly")
    if missing_policy not in {"error", "skip"}:
        raise ValueError("missing_policy must be 'error' or 'skip'")
    density = float(water_density_kg_m3)
    gravity = float(gravity_m_s2)
    if not math.isfinite(density) or density <= 0.0:
        raise ValueError("water_density_kg_m3 must be finite and positive")
    if not math.isfinite(gravity) or gravity <= 0.0:
        raise ValueError("gravity_m_s2 must be finite and positive")

    included: list[tuple[int, int, float, float]] = []
    for row_index in range(rows):
        for column_index in range(columns):
            if ocean_mask is not None and not ocean_mask[row_index][column_index]:
                continue
            area = float(cell_area_m2[row_index][column_index])
            fraction = (
                1.0
                if cell_ocean_fraction is None
                else float(cell_ocean_fraction[row_index][column_index])
            )
            if not math.isfinite(area) or area <= 0.0:
                raise ValueError("cell areas must be finite and positive")
            if not math.isfinite(fraction) or not 0.0 <= fraction <= 1.0:
                raise ValueError("cell ocean fractions must lie in [0, 1]")
            if fraction == 0.0:
                continue
            raw_pressure = pressure_anomaly_pa[row_index][column_index]
            if raw_pressure is None or not math.isfinite(float(raw_pressure)):
                if missing_policy == "error":
                    raise ValueError("included ocean cell has missing pressure anomaly")
                continue
            included.append((row_index, column_index, float(raw_pressure), area * fraction))
    if not included:
        raise ValueError("no valid ocean cells remain for inverse-barometer calculation")

    included_area = math.fsum(item[3] for item in included)
    mean_pressure = (
        math.fsum(item[2] * item[3] for item in included) / included_area
        if remove_ocean_mean
        else 0.0
    )
    sea_level: list[list[float | None]] = [[None] * columns for _ in range(rows)]
    mass_terms = []
    for row_index, column_index, pressure, effective_area in included:
        anomaly = -(pressure - mean_pressure) / (density * gravity)
        sea_level[row_index][column_index] = anomaly
        mass_terms.append(density * anomaly * effective_area)
    return InverseBarometerResult(
        sea_level_anomaly_m=tuple(tuple(row) for row in sea_level),
        ocean_mean_pressure_anomaly_pa=mean_pressure,
        included_area_m2=included_area,
        net_surface_mass_anomaly_kg=math.fsum(mass_terms),
        remove_ocean_mean=remove_ocean_mean,
    )
