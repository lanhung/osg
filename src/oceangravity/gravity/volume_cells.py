"""Reference gravity integration for discretized three-dimensional density anomalies."""

from __future__ import annotations

import math
from collections.abc import Sequence
from numbers import Real

from oceangravity.constants import GRAVITATIONAL_CONSTANT

from .point_mass import Vector3, _as_finite_vector3


def volume_cell_gravity(
    density_kg_m3: Sequence[float],
    cell_centers_xyz_m: Sequence[Sequence[float]],
    cell_volumes_m3: float | Sequence[float],
    observation_xyz_m: Sequence[float],
) -> Vector3:
    """Sum gravitational acceleration from constant-density volume cells.

    Each cell is represented by a point mass at its centre. This is a transparent
    reference discretization; callers must demonstrate spatial convergence for a
    physical result. Densities may be signed anomalies. Volumes must be positive.
    """

    cell_count = len(density_kg_m3)
    if len(cell_centers_xyz_m) != cell_count:
        raise ValueError("density and cell-centre arrays must have equal length")
    observation = _as_finite_vector3("observation_xyz_m", observation_xyz_m)

    if isinstance(cell_volumes_m3, Real) and not isinstance(cell_volumes_m3, bool):
        volume = float(cell_volumes_m3)
        if not math.isfinite(volume) or volume <= 0.0:
            raise ValueError("cell volume must be finite and greater than zero")
        volumes = None
    else:
        volumes = cell_volumes_m3
        if len(volumes) != cell_count:
            raise ValueError("cell-volume array must match density length")

    contributions_x: list[float] = []
    contributions_y: list[float] = []
    contributions_z: list[float] = []
    for index in range(cell_count):
        density = float(density_kg_m3[index])
        if not math.isfinite(density):
            raise ValueError(f"density at cell {index} must be finite")
        cell_volume = volume if volumes is None else float(volumes[index])
        if not math.isfinite(cell_volume) or cell_volume <= 0.0:
            raise ValueError(f"volume at cell {index} must be finite and greater than zero")
        center = _as_finite_vector3(f"cell_centers_xyz_m[{index}]", cell_centers_xyz_m[index])
        mass = density * cell_volume
        if mass == 0.0:
            continue

        displacement_x = center[0] - observation[0]
        displacement_y = center[1] - observation[1]
        displacement_z = center[2] - observation[2]
        distance_squared = displacement_x**2 + displacement_y**2 + displacement_z**2
        if distance_squared == 0.0:
            raise ValueError(
                f"nonzero point-cell mass at observation location for cell {index}; refine or "
                "integrate the containing cell analytically"
            )
        scale = (
            GRAVITATIONAL_CONSTANT.value
            * mass
            / (distance_squared * math.sqrt(distance_squared))
        )
        contributions_x.append(scale * displacement_x)
        contributions_y.append(scale * displacement_y)
        contributions_z.append(scale * displacement_z)

    return (
        math.fsum(contributions_x),
        math.fsum(contributions_y),
        math.fsum(contributions_z),
    )

