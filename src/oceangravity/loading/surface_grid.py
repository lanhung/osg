"""Auditable direct gravity from local planar gridded surface loads."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from oceangravity.constants import GRAVITATIONAL_CONSTANT, REFERENCE_SEAWATER_DENSITY
from oceangravity.gravity.point_mass import Vector3, _as_finite_vector3

OptionalGrid = Sequence[Sequence[float | None]]


@dataclass(frozen=True, slots=True)
class SurfaceLoadResult:
    """Direct-attraction result plus the accounting needed for data-quality review."""

    gravity_m_s2: Vector3
    included_area_m2: float
    included_mass_kg: float
    included_cells: int
    skipped_masked_cells: int
    skipped_missing_cells: int


def sea_level_to_surface_density(
    sea_level_anomaly_m: OptionalGrid,
    water_density_kg_m3: float = REFERENCE_SEAWATER_DENSITY.value,
) -> tuple[tuple[float | None, ...], ...]:
    """Convert sea-level anomaly to signed surface density, preserving missing cells."""

    density = float(water_density_kg_m3)
    if not math.isfinite(density) or density <= 0.0:
        raise ValueError("water_density_kg_m3 must be finite and greater than zero")
    width = _validate_grid_shape(sea_level_anomaly_m, "sea_level_anomaly_m")
    converted = []
    for row_index, row in enumerate(sea_level_anomaly_m):
        converted_row = []
        for column_index in range(width):
            value = row[column_index]
            if value is None:
                converted_row.append(None)
                continue
            anomaly = float(value)
            if not math.isfinite(anomaly):
                converted_row.append(None)
                continue
            converted_row.append(anomaly * density)
        converted.append(tuple(converted_row))
    return tuple(converted)


def surface_load_gravity_planar(
    surface_density_kg_m2: OptionalGrid,
    x_edges_m: Sequence[float],
    y_edges_m: Sequence[float],
    load_z_m: float,
    observation_xyz_m: Sequence[float],
    *,
    water_mask: Sequence[Sequence[bool]] | None = None,
    missing_policy: str = "error",
) -> SurfaceLoadResult:
    """Approximate each planar grid cell by a point mass at its area centroid.

    Grid rows follow increasing ``y`` and columns follow increasing ``x``. Edges may
    be irregular but must be strictly increasing. ``water_mask=False`` always skips
    a cell. Missing values are ``None`` or non-finite numbers and either raise or are
    counted/skipped according to ``missing_policy``.
    """

    if missing_policy not in {"error", "skip"}:
        raise ValueError("missing_policy must be 'error' or 'skip'")
    column_count = _validate_grid_shape(surface_density_kg_m2, "surface_density_kg_m2")
    row_count = len(surface_density_kg_m2)
    x_edges = _validate_edges(x_edges_m, column_count + 1, "x_edges_m")
    y_edges = _validate_edges(y_edges_m, row_count + 1, "y_edges_m")
    if water_mask is not None:
        mask_width = _validate_grid_shape(water_mask, "water_mask")
        if len(water_mask) != row_count or mask_width != column_count:
            raise ValueError("water_mask shape must match surface-density grid")
        if any(not isinstance(value, bool) for row in water_mask for value in row):
            raise ValueError("water_mask must contain booleans")

    load_z = float(load_z_m)
    if not math.isfinite(load_z):
        raise ValueError("load_z_m must be finite")
    observation = _as_finite_vector3("observation_xyz_m", observation_xyz_m)
    contributions_x: list[float] = []
    contributions_y: list[float] = []
    contributions_z: list[float] = []
    areas: list[float] = []
    masses: list[float] = []
    included_cells = 0
    skipped_masked_cells = 0
    skipped_missing_cells = 0

    for row_index in range(row_count):
        step_y = y_edges[row_index + 1] - y_edges[row_index]
        center_y = 0.5 * (y_edges[row_index + 1] + y_edges[row_index])
        for column_index in range(column_count):
            if water_mask is not None and not water_mask[row_index][column_index]:
                skipped_masked_cells += 1
                continue
            raw_density = surface_density_kg_m2[row_index][column_index]
            if raw_density is None or not math.isfinite(float(raw_density)):
                if missing_policy == "error":
                    raise ValueError(
                        f"missing surface density at row {row_index}, column {column_index}"
                    )
                skipped_missing_cells += 1
                continue
            density = float(raw_density)
            step_x = x_edges[column_index + 1] - x_edges[column_index]
            center_x = 0.5 * (x_edges[column_index + 1] + x_edges[column_index])
            area = step_x * step_y
            mass = density * area
            included_cells += 1
            areas.append(area)
            masses.append(mass)
            if mass == 0.0:
                continue

            displacement_x = center_x - observation[0]
            displacement_y = center_y - observation[1]
            displacement_z = load_z - observation[2]
            distance_squared = (
                displacement_x**2 + displacement_y**2 + displacement_z**2
            )
            if distance_squared == 0.0:
                raise ValueError(
                    "nonzero point-cell mass at observation location; refine or use an "
                    "analytic containing-cell treatment"
                )
            scale = (
                GRAVITATIONAL_CONSTANT.value
                * mass
                / (distance_squared * math.sqrt(distance_squared))
            )
            contributions_x.append(scale * displacement_x)
            contributions_y.append(scale * displacement_y)
            contributions_z.append(scale * displacement_z)

    return SurfaceLoadResult(
        gravity_m_s2=(
            math.fsum(contributions_x),
            math.fsum(contributions_y),
            math.fsum(contributions_z),
        ),
        included_area_m2=math.fsum(areas),
        included_mass_kg=math.fsum(masses),
        included_cells=included_cells,
        skipped_masked_cells=skipped_masked_cells,
        skipped_missing_cells=skipped_missing_cells,
    )


def _validate_grid_shape(grid: Sequence[Sequence[object]], name: str) -> int:
    if len(grid) == 0:
        raise ValueError(f"{name} must have at least one row")
    width = len(grid[0])
    if width == 0:
        raise ValueError(f"{name} must have at least one column")
    if any(len(row) != width for row in grid):
        raise ValueError(f"{name} must be rectangular")
    return width


def _validate_edges(edges: Sequence[float], expected_length: int, name: str) -> tuple[float, ...]:
    if len(edges) != expected_length:
        raise ValueError(f"{name} must contain {expected_length} values")
    values = tuple(float(value) for value in edges)
    if not all(math.isfinite(value) for value in values):
        raise ValueError(f"{name} must contain finite values")
    if any(values[index + 1] <= values[index] for index in range(len(values) - 1)):
        raise ValueError(f"{name} must be strictly increasing")
    return values

