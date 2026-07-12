"""Gravity of a radially symmetric Gaussian surface-mass anomaly."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from oceangravity.constants import GRAVITATIONAL_CONSTANT

from .point_mass import Vector3, _as_finite_vector3


@dataclass(frozen=True, slots=True)
class GaussianSurfaceResponse:
    gravity_m_s2: Vector3
    vertical_gravity_gradient_s2: float


def _gaussian_axis_geometry_factor(separation_over_scale: float) -> float:
    """Return the stable dimensionless axial field factor for a Gaussian sheet."""

    q = separation_over_scale
    if q < 12.0:
        scaled_erfc = math.exp(0.5 * q**2) * math.erfc(q / math.sqrt(2.0))
        return 1.0 - math.sqrt(math.pi / 2.0) * q * scaled_erfc

    # Far-field expansion after cancellation of the leading erfcx term.
    inverse_q_squared = 1.0 / q**2
    return inverse_q_squared * (
        1.0
        + inverse_q_squared
        * (
            -3.0
            + inverse_q_squared * (15.0 + inverse_q_squared * (-105.0 + inverse_q_squared * 945.0))
        )
    )


def gaussian_vertical_gravity_on_axis(
    peak_surface_density_kg_m2: float,
    scale_m: float,
    anomaly_z_m: float,
    observation_z_m: float,
) -> float:
    """Return axial vertical gravity of an infinite 2-D Gaussian surface anomaly.

    Surface density is ``sigma(r) = sigma_0 exp[-r^2 / (2 scale^2)]``. The total
    signed mass is ``2 pi sigma_0 scale^2``.
    """

    density = float(peak_surface_density_kg_m2)
    scale = float(scale_m)
    anomaly_z = float(anomaly_z_m)
    observation_z = float(observation_z_m)
    for name, value in (
        ("peak_surface_density_kg_m2", density),
        ("scale_m", scale),
        ("anomaly_z_m", anomaly_z),
        ("observation_z_m", observation_z),
    ):
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")
    if scale <= 0.0:
        raise ValueError("scale_m must be greater than zero")
    signed_separation = anomaly_z - observation_z
    if signed_separation == 0.0:
        raise ValueError("Gaussian-sheet gravity is discontinuous in the anomaly plane")

    geometry_factor = _gaussian_axis_geometry_factor(abs(signed_separation) / scale)
    return (
        math.copysign(1.0, signed_separation)
        * 2.0
        * math.pi
        * GRAVITATIONAL_CONSTANT.value
        * density
        * geometry_factor
    )


def gaussian_surface_gravity_numerical(
    peak_surface_density_kg_m2: float,
    scale_m: float,
    anomaly_center_xyz_m: Sequence[float],
    observation_xyz_m: Sequence[float],
    *,
    radial_cells: int = 256,
    angular_cells: int = 256,
    cutoff_sigma: float = 8.0,
) -> Vector3:
    """Integrate a Gaussian surface anomaly in polar midpoint cells.

    The infinite anomaly is truncated at ``cutoff_sigma * scale_m``. The omitted
    mass fraction is exactly ``exp(-cutoff_sigma^2 / 2)``.
    """

    return gaussian_surface_response_numerical(
        peak_surface_density_kg_m2,
        scale_m,
        anomaly_center_xyz_m,
        observation_xyz_m,
        radial_cells=radial_cells,
        angular_cells=angular_cells,
        cutoff_sigma=cutoff_sigma,
    ).gravity_m_s2


def gaussian_surface_response_numerical(
    peak_surface_density_kg_m2: float,
    scale_m: float,
    anomaly_center_xyz_m: Sequence[float],
    observation_xyz_m: Sequence[float],
    *,
    radial_cells: int = 256,
    angular_cells: int = 256,
    cutoff_sigma: float = 8.0,
) -> GaussianSurfaceResponse:
    """Integrate gravity vector and ``Tzz`` in the same polar-cell pass."""

    density = float(peak_surface_density_kg_m2)
    scale = float(scale_m)
    cutoff = float(cutoff_sigma)
    for name, value in (
        ("peak_surface_density_kg_m2", density),
        ("scale_m", scale),
        ("cutoff_sigma", cutoff),
    ):
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")
    if scale <= 0.0:
        raise ValueError("scale_m must be greater than zero")
    if cutoff <= 0.0:
        raise ValueError("cutoff_sigma must be greater than zero")
    if isinstance(radial_cells, bool) or not isinstance(radial_cells, int) or radial_cells <= 0:
        raise ValueError("radial_cells must be a positive integer")
    if isinstance(angular_cells, bool) or not isinstance(angular_cells, int) or angular_cells < 3:
        raise ValueError("angular_cells must be an integer of at least three")

    center = _as_finite_vector3("anomaly_center_xyz_m", anomaly_center_xyz_m)
    observation = _as_finite_vector3("observation_xyz_m", observation_xyz_m)
    if observation[2] == center[2]:
        raise ValueError("Gaussian-sheet gravity is discontinuous in the anomaly plane")

    maximum_radius = cutoff * scale
    radial_step = maximum_radius / radial_cells
    angular_step = 2.0 * math.pi / angular_cells
    base_scale = GRAVITATIONAL_CONSTANT.value * density
    displacement_z = center[2] - observation[2]
    acceleration_x = 0.0
    acceleration_y = 0.0
    acceleration_z = 0.0
    gradient_zz_terms: list[float] = []

    for radial_index in range(radial_cells):
        local_radius = (radial_index + 0.5) * radial_step
        local_density_factor = math.exp(-0.5 * (local_radius / scale) ** 2)
        cell_area = local_radius * radial_step * angular_step
        for angular_index in range(angular_cells):
            angle = (angular_index + 0.5) * angular_step
            source_x = center[0] + local_radius * math.cos(angle)
            source_y = center[1] + local_radius * math.sin(angle)
            displacement_x = source_x - observation[0]
            displacement_y = source_y - observation[1]
            distance_squared = displacement_x**2 + displacement_y**2 + displacement_z**2
            inverse_distance_cubed = 1.0 / (distance_squared * math.sqrt(distance_squared))
            cell_scale = base_scale * local_density_factor * cell_area * inverse_distance_cubed
            acceleration_x += cell_scale * displacement_x
            acceleration_y += cell_scale * displacement_y
            acceleration_z += cell_scale * displacement_z
            gradient_zz_terms.append(
                base_scale
                * local_density_factor
                * cell_area
                * (
                    3.0 * displacement_z**2 * inverse_distance_cubed / distance_squared
                    - inverse_distance_cubed
                )
            )

    return GaussianSurfaceResponse(
        gravity_m_s2=(acceleration_x, acceleration_y, acceleration_z),
        vertical_gravity_gradient_s2=math.fsum(gradient_zz_terms),
    )
