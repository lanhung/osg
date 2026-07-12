"""Deterministic midpoint integration for a uniform horizontal disk."""

from __future__ import annotations

import math
from collections.abc import Sequence

from oceangravity.constants import GRAVITATIONAL_CONSTANT

from .point_mass import Vector3, _as_finite_vector3


def disk_gravity_numerical(
    surface_density_kg_m2: float,
    radius_m: float,
    disk_center_xyz_m: Sequence[float],
    observation_xyz_m: Sequence[float],
    *,
    radial_cells: int = 128,
    angular_cells: int = 256,
) -> Vector3:
    """Integrate the gravity vector of a uniform disk using polar midpoint cells.

    This transparent reference integrator prioritizes validation over production
    throughput. The radial midpoint rule exactly preserves total disk area because
    each cell uses the polar Jacobian ``r``. Production gridded loads will use a
    separately benchmarked vectorized/chunked implementation.
    """

    density = float(surface_density_kg_m2)
    radius = float(radius_m)
    if not math.isfinite(density):
        raise ValueError("surface_density_kg_m2 must be finite")
    if not math.isfinite(radius) or radius <= 0.0:
        raise ValueError("radius_m must be finite and greater than zero")
    if isinstance(radial_cells, bool) or not isinstance(radial_cells, int) or radial_cells <= 0:
        raise ValueError("radial_cells must be a positive integer")
    if isinstance(angular_cells, bool) or not isinstance(angular_cells, int) or angular_cells < 3:
        raise ValueError("angular_cells must be an integer of at least three")

    center = _as_finite_vector3("disk_center_xyz_m", disk_center_xyz_m)
    observation = _as_finite_vector3("observation_xyz_m", observation_xyz_m)
    in_plane_radius = math.hypot(observation[0] - center[0], observation[1] - center[1])
    if observation[2] == center[2] and in_plane_radius <= radius:
        raise ValueError("thin-disk gravity is singular/discontinuous within the disk plane")

    radial_step = radius / radial_cells
    angular_step = 2.0 * math.pi / angular_cells
    scale = GRAVITATIONAL_CONSTANT.value * density
    acceleration_x = 0.0
    acceleration_y = 0.0
    acceleration_z = 0.0

    for radial_index in range(radial_cells):
        local_radius = (radial_index + 0.5) * radial_step
        cell_area = local_radius * radial_step * angular_step
        for angular_index in range(angular_cells):
            angle = (angular_index + 0.5) * angular_step
            source_x = center[0] + local_radius * math.cos(angle)
            source_y = center[1] + local_radius * math.sin(angle)
            displacement_x = source_x - observation[0]
            displacement_y = source_y - observation[1]
            displacement_z = center[2] - observation[2]
            distance_squared = (
                displacement_x**2 + displacement_y**2 + displacement_z**2
            )
            inverse_distance_cubed = 1.0 / (
                distance_squared * math.sqrt(distance_squared)
            )
            cell_scale = scale * cell_area * inverse_distance_cubed
            acceleration_x += cell_scale * displacement_x
            acceleration_y += cell_scale * displacement_y
            acceleration_z += cell_scale * displacement_z

    return acceleration_x, acceleration_y, acceleration_z

