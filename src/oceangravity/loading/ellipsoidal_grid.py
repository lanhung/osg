"""Reference direct attraction from surface loads on the WGS 84 ellipsoid."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from oceangravity.constants import (
    GRAVITATIONAL_CONSTANT,
    WGS84_INVERSE_FLATTENING,
    WGS84_SEMI_MAJOR_AXIS,
)
from oceangravity.gravity.gradient import Matrix3, gravity_gradient_tensor
from oceangravity.gravity.point_mass import Vector3

from .surface_grid import OptionalGrid, _validate_cell_load_fraction, _validate_grid_shape


@dataclass(frozen=True, slots=True)
class EllipsoidalSurfaceLoadResult:
    """ECEF attraction, geodetic-up projection, and cell accounting."""

    gravity_ecef_m_s2: Vector3
    geodetic_up_gravity_m_s2: float
    gravity_gradient_ecef_s2: Matrix3
    geodetic_up_gravity_gradient_s2: float
    included_area_m2: float
    included_mass_kg: float
    included_cells: int
    skipped_masked_cells: int
    skipped_zero_fraction_cells: int
    skipped_missing_cells: int


def surface_load_gravity_wgs84(
    surface_density_kg_m2: OptionalGrid,
    latitude_edges_deg: Sequence[float],
    longitude_edges_deg_unwrapped: Sequence[float],
    observation_latitude_deg: float,
    observation_longitude_deg: float,
    observation_height_m: float,
    *,
    load_height_m: float = 0.0,
    water_mask: Sequence[Sequence[bool]] | None = None,
    cell_load_fraction: Sequence[Sequence[float]] | None = None,
    missing_policy: str = "error",
) -> EllipsoidalSurfaceLoadResult:
    """Approximate WGS 84 cells by masses at exact-area latitude centroids.

    Cell areas integrate the ellipsoidal surface element exactly. Longitude
    centroids are midpoints; latitude centroids bisect ellipsoidal cell area.
    Source and observer coordinates use geodetic latitude and ellipsoidal height.
    """

    if missing_policy not in {"error", "skip"}:
        raise ValueError("missing_policy must be 'error' or 'skip'")
    columns = _validate_grid_shape(surface_density_kg_m2, "surface_density_kg_m2")
    rows = len(surface_density_kg_m2)
    latitudes = _validate_latitudes(latitude_edges_deg, rows + 1)
    longitudes = _validate_longitudes(longitude_edges_deg_unwrapped, columns + 1)
    if water_mask is not None:
        mask_columns = _validate_grid_shape(water_mask, "water_mask")
        if len(water_mask) != rows or mask_columns != columns:
            raise ValueError("water_mask shape must match surface-density grid")
        if any(not isinstance(value, bool) for row in water_mask for value in row):
            raise ValueError("water_mask must contain booleans")
    fractions = _validate_cell_load_fraction(cell_load_fraction, rows, columns)

    observation_latitude = _validate_geodetic_latitude(observation_latitude_deg)
    observation_longitude = math.radians(float(observation_longitude_deg))
    observation_height = float(observation_height_m)
    source_height = float(load_height_m)
    if not all(
        math.isfinite(value)
        for value in (observation_longitude, observation_height, source_height)
    ):
        raise ValueError("longitude and heights must be finite")
    observation = _geodetic_ecef(
        observation_latitude, observation_longitude, observation_height
    )
    up = _geodetic_up(observation_latitude, observation_longitude)

    gravity_x: list[float] = []
    gravity_y: list[float] = []
    gravity_z: list[float] = []
    gradient_terms: list[list[float]] = [[] for _ in range(9)]
    areas: list[float] = []
    masses: list[float] = []
    included_cells = 0
    skipped_masked_cells = 0
    skipped_zero_fraction_cells = 0
    skipped_missing_cells = 0

    for row_index in range(rows):
        south = math.radians(latitudes[row_index])
        north = math.radians(latitudes[row_index + 1])
        south_area_coordinate = _ellipsoid_area_primitive(math.sin(south))
        north_area_coordinate = _ellipsoid_area_primitive(math.sin(north))
        centroid_area_coordinate = 0.5 * (south_area_coordinate + north_area_coordinate)
        centroid_latitude = _latitude_from_area_coordinate(
            centroid_area_coordinate, south, north
        )
        for column_index in range(columns):
            if water_mask is not None and not water_mask[row_index][column_index]:
                skipped_masked_cells += 1
                continue
            fraction = fractions[row_index][column_index] if fractions is not None else 1.0
            if fraction == 0.0:
                skipped_zero_fraction_cells += 1
                continue
            raw_density = surface_density_kg_m2[row_index][column_index]
            if raw_density is None or not math.isfinite(float(raw_density)):
                if missing_policy == "error":
                    raise ValueError(
                        f"missing surface density at row {row_index}, column {column_index}"
                    )
                skipped_missing_cells += 1
                continue
            west = math.radians(longitudes[column_index])
            east = math.radians(longitudes[column_index + 1])
            area = (
                (east - west)
                * (north_area_coordinate - south_area_coordinate)
                * fraction
            )
            mass = float(raw_density) * area
            included_cells += 1
            areas.append(area)
            masses.append(mass)
            if mass == 0.0:
                continue
            source = _geodetic_ecef(
                centroid_latitude, 0.5 * (west + east), source_height
            )
            displacement = tuple(source[index] - observation[index] for index in range(3))
            distance_squared = math.fsum(value * value for value in displacement)
            if distance_squared == 0.0:
                raise ValueError("nonzero point-cell mass at the observation location")
            scale = GRAVITATIONAL_CONSTANT.value * mass / (
                distance_squared * math.sqrt(distance_squared)
            )
            gravity_x.append(scale * displacement[0])
            gravity_y.append(scale * displacement[1])
            gravity_z.append(scale * displacement[2])
            tensor = gravity_gradient_tensor(mass, source, observation)
            for row in range(3):
                for column in range(3):
                    gradient_terms[3 * row + column].append(tensor[row][column])

    gravity = (math.fsum(gravity_x), math.fsum(gravity_y), math.fsum(gravity_z))
    gradient_rows = tuple(
        tuple(math.fsum(gradient_terms[3 * row + column]) for column in range(3))
        for row in range(3)
    )
    gradient: Matrix3 = (gradient_rows[0], gradient_rows[1], gradient_rows[2])
    up_gradient = math.fsum(
        up[row] * gradient[row][column] * up[column]
        for row in range(3)
        for column in range(3)
    )
    return EllipsoidalSurfaceLoadResult(
        gravity_ecef_m_s2=gravity,
        geodetic_up_gravity_m_s2=math.fsum(
            gravity[index] * up[index] for index in range(3)
        ),
        gravity_gradient_ecef_s2=gradient,
        geodetic_up_gravity_gradient_s2=up_gradient,
        included_area_m2=math.fsum(areas),
        included_mass_kg=math.fsum(masses),
        included_cells=included_cells,
        skipped_masked_cells=skipped_masked_cells,
        skipped_zero_fraction_cells=skipped_zero_fraction_cells,
        skipped_missing_cells=skipped_missing_cells,
    )


def _ellipsoid_parameters() -> tuple[float, float]:
    semi_major = WGS84_SEMI_MAJOR_AXIS.value
    flattening = 1.0 / WGS84_INVERSE_FLATTENING.value
    eccentricity_squared = flattening * (2.0 - flattening)
    return semi_major, eccentricity_squared


def _ellipsoid_area_primitive(sine_latitude: float) -> float:
    semi_major, eccentricity_squared = _ellipsoid_parameters()
    eccentricity = math.sqrt(eccentricity_squared)
    denominator = 1.0 - eccentricity_squared * sine_latitude**2
    integral = 0.5 * (
        sine_latitude / denominator
        + math.atanh(eccentricity * sine_latitude) / eccentricity
    )
    return semi_major**2 * (1.0 - eccentricity_squared) * integral


def _latitude_from_area_coordinate(target: float, south: float, north: float) -> float:
    lower, upper = south, north
    for _ in range(60):
        midpoint = 0.5 * (lower + upper)
        if _ellipsoid_area_primitive(math.sin(midpoint)) < target:
            lower = midpoint
        else:
            upper = midpoint
    return 0.5 * (lower + upper)


def _geodetic_ecef(latitude: float, longitude: float, height: float) -> Vector3:
    semi_major, eccentricity_squared = _ellipsoid_parameters()
    sine_latitude = math.sin(latitude)
    cosine_latitude = math.cos(latitude)
    prime_vertical_radius = semi_major / math.sqrt(
        1.0 - eccentricity_squared * sine_latitude**2
    )
    return (
        (prime_vertical_radius + height) * cosine_latitude * math.cos(longitude),
        (prime_vertical_radius + height) * cosine_latitude * math.sin(longitude),
        (prime_vertical_radius * (1.0 - eccentricity_squared) + height) * sine_latitude,
    )


def _geodetic_up(latitude: float, longitude: float) -> Vector3:
    return (
        math.cos(latitude) * math.cos(longitude),
        math.cos(latitude) * math.sin(longitude),
        math.sin(latitude),
    )


def _validate_geodetic_latitude(value: float) -> float:
    latitude = float(value)
    if not math.isfinite(latitude) or not -90.0 <= latitude <= 90.0:
        raise ValueError("geodetic latitude must be finite and within [-90, 90] degrees")
    return math.radians(latitude)


def _validate_latitudes(edges: Sequence[float], expected: int) -> tuple[float, ...]:
    if len(edges) != expected:
        raise ValueError(f"latitude edges must contain {expected} values")
    values = tuple(float(value) for value in edges)
    if not all(math.isfinite(value) and -90.0 <= value <= 90.0 for value in values):
        raise ValueError("latitude edges must be finite and within [-90, 90] degrees")
    if any(values[index + 1] <= values[index] for index in range(len(values) - 1)):
        raise ValueError("latitude edges must be strictly increasing")
    return values


def _validate_longitudes(edges: Sequence[float], expected: int) -> tuple[float, ...]:
    if len(edges) != expected:
        raise ValueError(f"longitude edges must contain {expected} values")
    values = tuple(float(value) for value in edges)
    if not all(math.isfinite(value) for value in values):
        raise ValueError("longitude edges must be finite")
    if any(values[index + 1] <= values[index] for index in range(len(values) - 1)):
        raise ValueError("unwrapped longitude edges must be strictly increasing")
    if values[-1] - values[0] > 360.0 + 1e-12:
        raise ValueError("longitude grid may span at most 360 degrees")
    return values
