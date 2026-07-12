"""Periodic finite-disk tide reference model."""

from __future__ import annotations

import math
from collections.abc import Sequence

from oceangravity.constants import REFERENCE_SEAWATER_DENSITY
from oceangravity.gravity import (
    disk_vertical_gravity_gradient_on_axis,
    disk_vertical_gravity_on_axis,
)

from .common import ScalarGravitySignal


def periodic_disk_tide(
    times_s: Sequence[float],
    *,
    sea_level_peak_amplitude_m: float,
    period_s: float,
    phase_rad: float,
    disk_radius_m: float,
    disk_z_m: float,
    observation_z_m: float,
    water_density_kg_m3: float = REFERENCE_SEAWATER_DENSITY.value,
) -> ScalarGravitySignal:
    """Return direct vertical gravity from a sinusoidal uniform sea-level disk.

    Positive sea-level anomaly adds surface mass ``rho_water * eta``. The source is
    intentionally simple: a horizontal, uniform, zero-thickness disk observed on
    its symmetry axis. It is a controlled atlas primitive, not a harmonic ocean
    tide model or an elastic loading solution.
    """

    times = tuple(float(value) for value in times_s)
    amplitude = float(sea_level_peak_amplitude_m)
    period = float(period_s)
    phase = float(phase_rad)
    density = float(water_density_kg_m3)
    for name, value in (
        ("sea_level_peak_amplitude_m", amplitude),
        ("period_s", period),
        ("phase_rad", phase),
        ("water_density_kg_m3", density),
    ):
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")
    if period <= 0.0:
        raise ValueError("period_s must be greater than zero")
    if density <= 0.0:
        raise ValueError("water_density_kg_m3 must be greater than zero")

    unit_sea_level_gravity = disk_vertical_gravity_on_axis(
        density,
        disk_radius_m,
        disk_z_m,
        observation_z_m,
    )
    unit_sea_level_gradient = disk_vertical_gravity_gradient_on_axis(
        density,
        disk_radius_m,
        disk_z_m,
        observation_z_m,
    )
    angular_frequency = 2.0 * math.pi / period
    sea_level = tuple(
        amplitude * math.cos(angular_frequency * time + phase) for time in times
    )
    gravity = tuple(unit_sea_level_gravity * value for value in sea_level)
    return ScalarGravitySignal(
        process_id="periodic_disk_tide",
        times_s=times,
        source_amplitude=sea_level,
        source_amplitude_unit="m sea-level anomaly",
        vertical_direct_gravity_m_s2=gravity,
        model_scope="direct attraction of a uniform finite disk; no elastic Earth response",
        vertical_direct_gravity_gradient_s2=tuple(
            unit_sea_level_gradient * value for value in sea_level
        ),
    )
