"""Gravity of a uniform finite horizontal rectangular surface load."""

from __future__ import annotations

import math
from collections.abc import Sequence

from oceangravity.constants import GRAVITATIONAL_CONSTANT

from .point_mass import Vector3, _as_finite_vector3


def rectangle_vertical_gravity_on_axis(
    surface_density_kg_m2: float,
    half_width_x_m: float,
    half_width_y_m: float,
    rectangle_z_m: float,
    observation_z_m: float,
) -> float:
    """Return the analytic vertical field through a rectangle's centre.

    ``half_width_x_m`` and ``half_width_y_m`` are positive half dimensions. The
    rectangle is horizontal and centred on the observation's x/y coordinates.
    The output is upward-positive SI acceleration.
    """

    values = {
        "surface_density_kg_m2": float(surface_density_kg_m2),
        "half_width_x_m": float(half_width_x_m),
        "half_width_y_m": float(half_width_y_m),
        "rectangle_z_m": float(rectangle_z_m),
        "observation_z_m": float(observation_z_m),
    }
    for name, value in values.items():
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")
    if values["half_width_x_m"] <= 0.0 or values["half_width_y_m"] <= 0.0:
        raise ValueError("rectangle half widths must be greater than zero")

    signed_separation = values["rectangle_z_m"] - values["observation_z_m"]
    if signed_separation == 0.0:
        raise ValueError("thin-rectangle gravity is discontinuous in the load plane")
    separation = abs(signed_separation)
    half_x = values["half_width_x_m"]
    half_y = values["half_width_y_m"]
    denominator = separation * math.sqrt(separation**2 + half_x**2 + half_y**2)
    solid_angle_quarter = math.atan2(half_x * half_y, denominator)
    direction = math.copysign(1.0, signed_separation)
    return (
        direction
        * 4.0
        * GRAVITATIONAL_CONSTANT.value
        * values["surface_density_kg_m2"]
        * solid_angle_quarter
    )


def rectangle_gravity_numerical(
    surface_density_kg_m2: float,
    half_width_x_m: float,
    half_width_y_m: float,
    rectangle_center_xyz_m: Sequence[float],
    observation_xyz_m: Sequence[float],
    *,
    cells_x: int = 128,
    cells_y: int = 128,
) -> Vector3:
    """Integrate a uniform rectangular surface load with Cartesian midpoint cells."""

    density = float(surface_density_kg_m2)
    half_x = float(half_width_x_m)
    half_y = float(half_width_y_m)
    for name, value in (
        ("surface_density_kg_m2", density),
        ("half_width_x_m", half_x),
        ("half_width_y_m", half_y),
    ):
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")
    if half_x <= 0.0 or half_y <= 0.0:
        raise ValueError("rectangle half widths must be greater than zero")
    for name, count in (("cells_x", cells_x), ("cells_y", cells_y)):
        if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
            raise ValueError(f"{name} must be a positive integer")

    center = _as_finite_vector3("rectangle_center_xyz_m", rectangle_center_xyz_m)
    observation = _as_finite_vector3("observation_xyz_m", observation_xyz_m)
    inside_x = abs(observation[0] - center[0]) <= half_x
    inside_y = abs(observation[1] - center[1]) <= half_y
    if observation[2] == center[2] and inside_x and inside_y:
        raise ValueError("thin-rectangle gravity is singular/discontinuous within the load plane")

    step_x = 2.0 * half_x / cells_x
    step_y = 2.0 * half_y / cells_y
    cell_scale_base = GRAVITATIONAL_CONSTANT.value * density * step_x * step_y
    displacement_z = center[2] - observation[2]
    acceleration_x = 0.0
    acceleration_y = 0.0
    acceleration_z = 0.0

    for index_x in range(cells_x):
        source_x = center[0] - half_x + (index_x + 0.5) * step_x
        displacement_x = source_x - observation[0]
        for index_y in range(cells_y):
            source_y = center[1] - half_y + (index_y + 0.5) * step_y
            displacement_y = source_y - observation[1]
            distance_squared = (
                displacement_x**2 + displacement_y**2 + displacement_z**2
            )
            inverse_distance_cubed = 1.0 / (
                distance_squared * math.sqrt(distance_squared)
            )
            cell_scale = cell_scale_base * inverse_distance_cubed
            acceleration_x += cell_scale * displacement_x
            acceleration_y += cell_scale * displacement_y
            acceleration_z += cell_scale * displacement_z

    return acceleration_x, acceleration_y, acceleration_z

