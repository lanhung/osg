"""Auditable direct gravity from surface loads on a spherical Earth."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from oceangravity.constants import GRAVITATIONAL_CONSTANT, MEAN_EARTH_RADIUS
from oceangravity.gravity.point_mass import Vector3

from .surface_grid import OptionalGrid, _validate_grid_shape


@dataclass(frozen=True, slots=True)
class SphericalSurfaceLoadResult:
    """ECEF direct attraction and source-grid accounting."""

    gravity_ecef_m_s2: Vector3
    radial_gravity_m_s2: float
    included_area_m2: float
    included_mass_kg: float
    included_cells: int
    skipped_masked_cells: int
    skipped_missing_cells: int


def surface_load_gravity_spherical(
    surface_density_kg_m2: OptionalGrid,
    latitude_edges_deg: Sequence[float],
    longitude_edges_deg_unwrapped: Sequence[float],
    observation_latitude_deg: float,
    observation_longitude_deg: float,
    observation_height_m: float,
    *,
    load_radius_m: float = MEAN_EARTH_RADIUS.value,
    water_mask: Sequence[Sequence[bool]] | None = None,
    missing_policy: str = "error",
) -> SphericalSurfaceLoadResult:
    """Approximate spherical cells by point masses at equal-area centroids.

    Rows increase with latitude and columns with *unwrapped* longitude. Thus a grid
    crossing the antimeridian can use edges such as ``[170, 180, 190]``. Cell area
    is exact on a sphere. Source locations use the midpoint in longitude and in
    ``sin(latitude)``, the natural equal-area coordinate.
    """

    if missing_policy not in {"error", "skip"}:
        raise ValueError("missing_policy must be 'error' or 'skip'")
    column_count = _validate_grid_shape(surface_density_kg_m2, "surface_density_kg_m2")
    row_count = len(surface_density_kg_m2)
    latitudes = _validate_latitudes(latitude_edges_deg, row_count + 1)
    longitudes = _validate_longitudes(longitude_edges_deg_unwrapped, column_count + 1)
    if water_mask is not None:
        mask_width = _validate_grid_shape(water_mask, "water_mask")
        if len(water_mask) != row_count or mask_width != column_count:
            raise ValueError("water_mask shape must match surface-density grid")
        if any(not isinstance(value, bool) for row in water_mask for value in row):
            raise ValueError("water_mask must contain booleans")

    observation_latitude = math.radians(float(observation_latitude_deg))
    observation_longitude = math.radians(float(observation_longitude_deg))
    observation_height = float(observation_height_m)
    load_radius = float(load_radius_m)
    for name, value in (
        ("observation_latitude_deg", float(observation_latitude_deg)),
        ("observation_longitude_deg", float(observation_longitude_deg)),
        ("observation_height_m", observation_height),
        ("load_radius_m", load_radius),
    ):
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")
    if not -90.0 <= float(observation_latitude_deg) <= 90.0:
        raise ValueError("observation latitude must be within [-90, 90] degrees")
    if load_radius <= 0.0 or load_radius + observation_height <= 0.0:
        raise ValueError("load and observation radii must be greater than zero")

    radial_unit = _radial_unit(observation_latitude, observation_longitude)
    observation_radius = load_radius + observation_height
    observation = tuple(observation_radius * component for component in radial_unit)
    contributions_x: list[float] = []
    contributions_y: list[float] = []
    contributions_z: list[float] = []
    areas: list[float] = []
    masses: list[float] = []
    included_cells = 0
    skipped_masked_cells = 0
    skipped_missing_cells = 0

    for row_index in range(row_count):
        latitude_south = math.radians(latitudes[row_index])
        latitude_north = math.radians(latitudes[row_index + 1])
        sine_south = math.sin(latitude_south)
        sine_north = math.sin(latitude_north)
        centroid_latitude = math.asin(0.5 * (sine_south + sine_north))
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
            longitude_west = math.radians(longitudes[column_index])
            longitude_east = math.radians(longitudes[column_index + 1])
            longitude_width = longitude_east - longitude_west
            centroid_longitude = 0.5 * (longitude_west + longitude_east)
            area = load_radius**2 * longitude_width * (sine_north - sine_south)
            mass = density * area
            included_cells += 1
            areas.append(area)
            masses.append(mass)
            if mass == 0.0:
                continue

            source_unit = _radial_unit(centroid_latitude, centroid_longitude)
            source = tuple(load_radius * component for component in source_unit)
            displacement = tuple(source[index] - observation[index] for index in range(3))
            distance_squared = math.fsum(component**2 for component in displacement)
            if distance_squared == 0.0:
                raise ValueError(
                    "nonzero spherical point-cell mass at observation location; refine or "
                    "use an analytic containing-cell treatment"
                )
            scale = (
                GRAVITATIONAL_CONSTANT.value
                * mass
                / (distance_squared * math.sqrt(distance_squared))
            )
            contributions_x.append(scale * displacement[0])
            contributions_y.append(scale * displacement[1])
            contributions_z.append(scale * displacement[2])

    gravity = (
        math.fsum(contributions_x),
        math.fsum(contributions_y),
        math.fsum(contributions_z),
    )
    radial_gravity = math.fsum(gravity[index] * radial_unit[index] for index in range(3))
    return SphericalSurfaceLoadResult(
        gravity_ecef_m_s2=gravity,
        radial_gravity_m_s2=radial_gravity,
        included_area_m2=math.fsum(areas),
        included_mass_kg=math.fsum(masses),
        included_cells=included_cells,
        skipped_masked_cells=skipped_masked_cells,
        skipped_missing_cells=skipped_missing_cells,
    )


def _radial_unit(latitude_rad: float, longitude_rad: float) -> Vector3:
    cosine_latitude = math.cos(latitude_rad)
    return (
        cosine_latitude * math.cos(longitude_rad),
        cosine_latitude * math.sin(longitude_rad),
        math.sin(latitude_rad),
    )


def _validate_latitudes(edges: Sequence[float], expected_length: int) -> tuple[float, ...]:
    if len(edges) != expected_length:
        raise ValueError(f"latitude_edges_deg must contain {expected_length} values")
    values = tuple(float(value) for value in edges)
    if not all(math.isfinite(value) and -90.0 <= value <= 90.0 for value in values):
        raise ValueError("latitude edges must be finite and within [-90, 90] degrees")
    if any(values[index + 1] <= values[index] for index in range(len(values) - 1)):
        raise ValueError("latitude edges must be strictly increasing")
    return values


def _validate_longitudes(edges: Sequence[float], expected_length: int) -> tuple[float, ...]:
    if len(edges) != expected_length:
        raise ValueError(f"longitude edges must contain {expected_length} values")
    values = tuple(float(value) for value in edges)
    if not all(math.isfinite(value) for value in values):
        raise ValueError("longitude edges must be finite")
    if any(values[index + 1] <= values[index] for index in range(len(values) - 1)):
        raise ValueError("unwrapped longitude edges must be strictly increasing")
    if values[-1] - values[0] > 360.0 + 1.0e-12:
        raise ValueError("longitude grid may span at most 360 degrees")
    return values

