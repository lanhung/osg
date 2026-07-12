"""Gravity-gradient tensors for point masses and discretized density anomalies."""

from __future__ import annotations

import math
from collections.abc import Sequence
from numbers import Real

from oceangravity.constants import GRAVITATIONAL_CONSTANT

from .point_mass import _as_finite_vector3

Matrix3 = tuple[
    tuple[float, float, float],
    tuple[float, float, float],
    tuple[float, float, float],
]


def gravity_gradient_tensor(
    mass_kg: float,
    source_xyz_m: Sequence[float],
    observation_xyz_m: Sequence[float],
) -> Matrix3:
    """Return ``T_ij = derivative(g_i) / derivative(x_observation_j)`` in s^-2.

    Coordinates follow the local Cartesian, upward-positive convention used by
    :func:`oceangravity.gravity.gravity_vector`. Outside the source the tensor is
    symmetric and trace-free.
    """

    mass = float(mass_kg)
    if not math.isfinite(mass):
        raise ValueError("mass_kg must be finite")
    source = _as_finite_vector3("source_xyz_m", source_xyz_m)
    observation = _as_finite_vector3("observation_xyz_m", observation_xyz_m)
    displacement = tuple(source[index] - observation[index] for index in range(3))
    distance_squared = math.fsum(component * component for component in displacement)
    if distance_squared == 0.0:
        raise ValueError("point-mass gravity gradient is singular at the source location")

    inverse_distance_cubed = 1.0 / (distance_squared * math.sqrt(distance_squared))
    inverse_distance_fifth = inverse_distance_cubed / distance_squared
    scale = GRAVITATIONAL_CONSTANT.value * mass
    rows = []
    for row in range(3):
        rows.append(
            tuple(
                scale
                * (
                    3.0
                    * displacement[row]
                    * displacement[column]
                    * inverse_distance_fifth
                    - (inverse_distance_cubed if row == column else 0.0)
                )
                for column in range(3)
            )
        )
    return rows[0], rows[1], rows[2]


def volume_cell_gravity_gradient(
    density_kg_m3: Sequence[float],
    cell_centers_xyz_m: Sequence[Sequence[float]],
    cell_volumes_m3: float | Sequence[float],
    observation_xyz_m: Sequence[float],
) -> Matrix3:
    """Sum gravity-gradient tensors from constant-density point-cell masses."""

    cell_count = len(density_kg_m3)
    if len(cell_centers_xyz_m) != cell_count:
        raise ValueError("density and cell-centre arrays must have equal length")
    observation = _as_finite_vector3("observation_xyz_m", observation_xyz_m)
    if isinstance(cell_volumes_m3, Real) and not isinstance(cell_volumes_m3, bool):
        shared_volume = float(cell_volumes_m3)
        if not math.isfinite(shared_volume) or shared_volume <= 0.0:
            raise ValueError("cell volume must be finite and greater than zero")
        volumes = None
    else:
        volumes = cell_volumes_m3
        if len(volumes) != cell_count:
            raise ValueError("cell-volume array must match density length")

    component_terms: list[list[float]] = [[] for _ in range(9)]
    for index in range(cell_count):
        density = float(density_kg_m3[index])
        if not math.isfinite(density):
            raise ValueError(f"density at cell {index} must be finite")
        volume = shared_volume if volumes is None else float(volumes[index])
        if not math.isfinite(volume) or volume <= 0.0:
            raise ValueError(f"volume at cell {index} must be finite and greater than zero")
        if density == 0.0:
            continue
        tensor = gravity_gradient_tensor(
            density * volume,
            cell_centers_xyz_m[index],
            observation,
        )
        for row in range(3):
            for column in range(3):
                component_terms[3 * row + column].append(tensor[row][column])

    rows = []
    for row in range(3):
        rows.append(
            tuple(math.fsum(component_terms[3 * row + column]) for column in range(3))
        )
    return rows[0], rows[1], rows[2]

