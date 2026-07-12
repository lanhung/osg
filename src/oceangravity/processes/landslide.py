"""Mass-conserving solid and optional water relocation for a submarine landslide."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from oceangravity.gravity import (
    gravity_gradient_tensor,
    gravity_vector,
    volume_cell_gravity,
    volume_cell_gravity_gradient,
)
from oceangravity.gravity.gradient import Matrix3
from oceangravity.gravity.point_mass import Vector3

from .common import ScalarGravitySignal


@dataclass(frozen=True, slots=True)
class MassRelocationResult:
    signal: ScalarGravitySignal
    final_gravity_change_m_s2: Vector3
    final_gravity_gradient_change_s2: Matrix3
    net_mass_anomaly_kg: float


def mass_conserving_submarine_landslide(
    times_s: Sequence[float],
    *,
    solid_mass_kg: float,
    solid_source_xyz_m: Sequence[float],
    solid_destination_xyz_m: Sequence[float],
    transition_start_s: float,
    transition_duration_s: float,
    observation_xyz_m: Sequence[float],
    displaced_water_mass_kg: float = 0.0,
    water_source_xyz_m: Sequence[float] | None = None,
    water_destination_xyz_m: Sequence[float] | None = None,
) -> MassRelocationResult:
    """Return gravity change relative to pre-slide state for conserved mass pairs.

    During transition fraction ``F``, solid anomalies are ``-F M`` at the source
    and ``+F M`` at the destination. An optional water pair follows the same rule.
    ``F`` is a half-cosine ramp with zero derivative at start and end.
    """

    times = tuple(float(value) for value in times_s)
    solid_mass = float(solid_mass_kg)
    water_mass = float(displaced_water_mass_kg)
    start = float(transition_start_s)
    duration = float(transition_duration_s)
    for name, value in (
        ("solid_mass_kg", solid_mass),
        ("displaced_water_mass_kg", water_mass),
        ("transition_start_s", start),
        ("transition_duration_s", duration),
    ):
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")
    if solid_mass <= 0.0:
        raise ValueError("solid_mass_kg must be greater than zero")
    if water_mass < 0.0:
        raise ValueError("displaced_water_mass_kg must be non-negative")
    if duration <= 0.0:
        raise ValueError("transition_duration_s must be greater than zero")
    if water_mass > 0.0 and (water_source_xyz_m is None or water_destination_xyz_m is None):
        raise ValueError("nonzero displaced water mass requires source and destination coordinates")

    gravity_terms = [
        gravity_vector(solid_mass, solid_destination_xyz_m, observation_xyz_m),
        gravity_vector(-solid_mass, solid_source_xyz_m, observation_xyz_m),
    ]
    gradient_terms = [
        gravity_gradient_tensor(solid_mass, solid_destination_xyz_m, observation_xyz_m),
        gravity_gradient_tensor(-solid_mass, solid_source_xyz_m, observation_xyz_m),
    ]
    if water_mass > 0.0:
        assert water_source_xyz_m is not None and water_destination_xyz_m is not None
        gravity_terms.extend(
            (
                gravity_vector(water_mass, water_destination_xyz_m, observation_xyz_m),
                gravity_vector(-water_mass, water_source_xyz_m, observation_xyz_m),
            )
        )
        gradient_terms.extend(
            (
                gravity_gradient_tensor(water_mass, water_destination_xyz_m, observation_xyz_m),
                gravity_gradient_tensor(-water_mass, water_source_xyz_m, observation_xyz_m),
            )
        )

    final_gravity_values = tuple(
        math.fsum(term[component] for term in gravity_terms) for component in range(3)
    )
    final_gravity: Vector3 = (
        final_gravity_values[0],
        final_gravity_values[1],
        final_gravity_values[2],
    )
    final_gradient_rows = tuple(
        tuple(math.fsum(term[row][column] for term in gradient_terms) for column in range(3))
        for row in range(3)
    )
    final_gradient: Matrix3 = (
        final_gradient_rows[0],
        final_gradient_rows[1],
        final_gradient_rows[2],
    )
    fractions = tuple(_half_cosine_fraction(time, start, duration) for time in times)
    signal = ScalarGravitySignal(
        process_id="mass_conserving_submarine_landslide",
        times_s=times,
        source_amplitude=fractions,
        source_amplitude_unit="dimensionless completed mass-relocation fraction",
        vertical_direct_gravity_m_s2=tuple(fraction * final_gravity[2] for fraction in fractions),
        model_scope=(
            "direct gravity/gradient from conserved point-mass relocation; no "
            "continuum slide or generated wave"
        ),
        vertical_direct_gravity_gradient_s2=tuple(
            fraction * final_gradient[2][2] for fraction in fractions
        ),
    )
    return MassRelocationResult(
        signal=signal,
        final_gravity_change_m_s2=final_gravity,
        final_gravity_gradient_change_s2=final_gradient,
        net_mass_anomaly_kg=0.0,
    )


def mass_conserving_gaussian_submarine_landslide(
    times_s: Sequence[float],
    *,
    solid_mass_kg: float,
    horizontal_scale_m: float,
    vertical_scale_m: float,
    solid_source_xyz_m: Sequence[float],
    solid_destination_xyz_m: Sequence[float],
    transition_start_s: float,
    transition_duration_s: float,
    observation_xyz_m: Sequence[float],
    cells_per_axis: int = 8,
    cutoff_sigma: float = 3.0,
) -> MassRelocationResult:
    """Relocate identical Gaussian solid volumes with exact discrete mass balance."""

    times = tuple(float(value) for value in times_s)
    solid_mass = float(solid_mass_kg)
    horizontal_scale = float(horizontal_scale_m)
    vertical_scale = float(vertical_scale_m)
    start = float(transition_start_s)
    duration = float(transition_duration_s)
    cutoff = float(cutoff_sigma)
    source = tuple(float(value) for value in solid_source_xyz_m)
    destination = tuple(float(value) for value in solid_destination_xyz_m)
    observation = tuple(float(value) for value in observation_xyz_m)
    if not all(
        math.isfinite(value)
        for value in (
            solid_mass,
            horizontal_scale,
            vertical_scale,
            start,
            duration,
            cutoff,
            *source,
            *destination,
            *observation,
        )
    ):
        raise ValueError("continuum landslide parameters must be finite")
    if len(source) != 3 or len(destination) != 3 or len(observation) != 3:
        raise ValueError("source, destination, and observation must have three coordinates")
    if solid_mass <= 0.0 or horizontal_scale <= 0.0 or vertical_scale <= 0.0:
        raise ValueError("mass and Gaussian scales must be positive")
    if duration <= 0.0 or cutoff <= 0.0:
        raise ValueError("transition duration and cutoff must be positive")
    if (
        isinstance(cells_per_axis, bool)
        or not isinstance(cells_per_axis, int)
        or cells_per_axis < 2
    ):
        raise ValueError("cells_per_axis must be an integer of at least two")

    step_horizontal = 2.0 * cutoff * horizontal_scale / cells_per_axis
    step_vertical = 2.0 * cutoff * vertical_scale / cells_per_axis
    horizontal = tuple(
        -cutoff * horizontal_scale + (index + 0.5) * step_horizontal
        for index in range(cells_per_axis)
    )
    vertical = tuple(
        -cutoff * vertical_scale + (index + 0.5) * step_vertical for index in range(cells_per_axis)
    )
    local_centers = []
    weights = []
    for x in horizontal:
        for y in horizontal:
            for z in vertical:
                local_centers.append((x, y, z))
                weights.append(
                    math.exp(
                        -0.5
                        * (
                            (x / horizontal_scale) ** 2
                            + (y / horizontal_scale) ** 2
                            + (z / vertical_scale) ** 2
                        )
                    )
                )
    cell_volume = step_horizontal**2 * step_vertical
    density_scale = solid_mass / (math.fsum(weights) * cell_volume)
    densities = tuple(-density_scale * weight for weight in weights) + tuple(
        density_scale * weight for weight in weights
    )
    centers = tuple(
        (source[0] + x, source[1] + y, source[2] + z) for x, y, z in local_centers
    ) + tuple(
        (destination[0] + x, destination[1] + y, destination[2] + z) for x, y, z in local_centers
    )
    final_gravity = volume_cell_gravity(densities, centers, cell_volume, observation)
    final_gradient = volume_cell_gravity_gradient(densities, centers, cell_volume, observation)
    fractions = tuple(_half_cosine_fraction(time, start, duration) for time in times)
    signal = ScalarGravitySignal(
        process_id="mass_conserving_gaussian_submarine_landslide",
        times_s=times,
        source_amplitude=fractions,
        source_amplitude_unit="dimensionless completed continuum mass-relocation fraction",
        vertical_direct_gravity_m_s2=tuple(fraction * final_gravity[2] for fraction in fractions),
        model_scope=(
            "direct gravity/gradient from identical signed Gaussian solid volumes; "
            "no entrainment or generated wave"
        ),
        vertical_direct_gravity_gradient_s2=tuple(
            fraction * final_gradient[2][2] for fraction in fractions
        ),
    )
    net_mass = math.fsum(density * cell_volume for density in densities)
    return MassRelocationResult(
        signal=signal,
        final_gravity_change_m_s2=final_gravity,
        final_gravity_gradient_change_s2=final_gradient,
        net_mass_anomaly_kg=net_mass,
    )


def _half_cosine_fraction(time_s: float, start_s: float, duration_s: float) -> float:
    if time_s <= start_s:
        return 0.0
    if time_s >= start_s + duration_s:
        return 1.0
    normalized = (time_s - start_s) / duration_s
    return 0.5 * (1.0 - math.cos(math.pi * normalized))
