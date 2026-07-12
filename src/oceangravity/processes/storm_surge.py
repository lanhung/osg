"""Asymmetric transient storm-surge surface-load reference model."""

from __future__ import annotations

import math
from collections.abc import Sequence

from oceangravity.constants import REFERENCE_SEAWATER_DENSITY
from oceangravity.gravity import disk_vertical_gravity_on_axis

from .common import ScalarGravitySignal


def asymmetric_gaussian_disk_surge(
    times_s: Sequence[float],
    *,
    peak_sea_level_anomaly_m: float,
    peak_time_s: float,
    rise_scale_s: float,
    fall_scale_s: float,
    disk_radius_m: float,
    disk_z_m: float,
    observation_z_m: float,
    water_density_kg_m3: float = REFERENCE_SEAWATER_DENSITY.value,
) -> ScalarGravitySignal:
    """Return direct gravity from a smooth asymmetric Gaussian surge pulse.

    Before the peak, ``eta=A exp[-0.5((t-t_peak)/tau_rise)^2]``; after the peak,
    ``tau_fall`` is used. Both branches meet with zero first derivative at the peak.
    Signed peak anomaly allows setup or setdown.
    """

    times = tuple(float(value) for value in times_s)
    amplitude = float(peak_sea_level_anomaly_m)
    peak_time = float(peak_time_s)
    rise_scale = float(rise_scale_s)
    fall_scale = float(fall_scale_s)
    density = float(water_density_kg_m3)
    for name, value in (
        ("peak_sea_level_anomaly_m", amplitude),
        ("peak_time_s", peak_time),
        ("rise_scale_s", rise_scale),
        ("fall_scale_s", fall_scale),
        ("water_density_kg_m3", density),
    ):
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")
    if rise_scale <= 0.0 or fall_scale <= 0.0:
        raise ValueError("rise_scale_s and fall_scale_s must be greater than zero")
    if density <= 0.0:
        raise ValueError("water_density_kg_m3 must be greater than zero")

    unit_sea_level_gravity = disk_vertical_gravity_on_axis(
        density,
        disk_radius_m,
        disk_z_m,
        observation_z_m,
    )
    sea_level = []
    for time in times:
        scale = rise_scale if time < peak_time else fall_scale
        standardized_time = (time - peak_time) / scale
        sea_level.append(amplitude * math.exp(-0.5 * standardized_time**2))
    sea_level_tuple = tuple(sea_level)
    return ScalarGravitySignal(
        process_id="asymmetric_gaussian_disk_storm_surge",
        times_s=times,
        source_amplitude=sea_level_tuple,
        source_amplitude_unit="m sea-level anomaly",
        vertical_direct_gravity_m_s2=tuple(
            unit_sea_level_gravity * value for value in sea_level_tuple
        ),
        model_scope="direct attraction of an asymmetric transient finite-disk load; no elastic response",
    )

