"""Translating Gaussian sea-surface expression of a mesoscale eddy."""

from __future__ import annotations

import math
from collections.abc import Sequence

from oceangravity.constants import REFERENCE_SEAWATER_DENSITY
from oceangravity.gravity import gaussian_surface_response_numerical

from .common import ScalarGravitySignal


def translating_gaussian_surface_eddy(
    times_s: Sequence[float],
    *,
    peak_sea_level_anomaly_m: float,
    horizontal_scale_m: float,
    translation_speed_x_m_s: float,
    closest_approach_y_m: float,
    passage_time_s: float,
    anomaly_z_m: float,
    observation_xyz_m: Sequence[float],
    water_density_kg_m3: float = REFERENCE_SEAWATER_DENSITY.value,
    radial_cells: int = 48,
    angular_cells: int = 72,
    cutoff_sigma: float = 8.0,
) -> ScalarGravitySignal:
    """Return direct gravity as a Gaussian SSH anomaly translates in local x.

    The eddy centre is ``(v(t-t_passage), closest_y, anomaly_z)``. The reported
    source amplitude is local SSH directly beneath/above the observation's x/y
    projection, while gravity integrates the complete translated Gaussian sheet.
    """

    times = tuple(float(value) for value in times_s)
    peak = float(peak_sea_level_anomaly_m)
    scale = float(horizontal_scale_m)
    speed = float(translation_speed_x_m_s)
    closest_y = float(closest_approach_y_m)
    passage_time = float(passage_time_s)
    anomaly_z = float(anomaly_z_m)
    density = float(water_density_kg_m3)
    observation = tuple(float(value) for value in observation_xyz_m)
    for name, value in (
        ("peak_sea_level_anomaly_m", peak),
        ("horizontal_scale_m", scale),
        ("translation_speed_x_m_s", speed),
        ("closest_approach_y_m", closest_y),
        ("passage_time_s", passage_time),
        ("anomaly_z_m", anomaly_z),
        ("water_density_kg_m3", density),
    ):
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")
    if len(observation) != 3 or not all(math.isfinite(value) for value in observation):
        raise ValueError("observation_xyz_m must contain three finite coordinates")
    if scale <= 0.0:
        raise ValueError("horizontal_scale_m must be greater than zero")
    if speed == 0.0:
        raise ValueError("translation_speed_x_m_s must be nonzero")
    if density <= 0.0:
        raise ValueError("water_density_kg_m3 must be greater than zero")

    local_sea_level = []
    vertical_gravity = []
    vertical_gradient = []
    for time in times:
        center_x = speed * (time - passage_time)
        center = (center_x, closest_y, anomaly_z)
        horizontal_offset_squared = (
            (observation[0] - center_x) ** 2 + (observation[1] - closest_y) ** 2
        )
        local_sea_level.append(
            peak * math.exp(-0.5 * horizontal_offset_squared / scale**2)
        )
        response = gaussian_surface_response_numerical(
            density * peak,
            scale,
            center,
            observation,
            radial_cells=radial_cells,
            angular_cells=angular_cells,
            cutoff_sigma=cutoff_sigma,
        )
        vertical_gravity.append(response.gravity_m_s2[2])
        vertical_gradient.append(response.vertical_gravity_gradient_s2)

    return ScalarGravitySignal(
        process_id="translating_gaussian_surface_eddy",
        times_s=times,
        source_amplitude=tuple(local_sea_level),
        source_amplitude_unit="m local sea-level anomaly at observation projection",
        vertical_direct_gravity_m_s2=tuple(vertical_gravity),
        model_scope="direct attraction of translating Gaussian SSH; no 3-D compensation or elastic response",
        vertical_direct_gravity_gradient_s2=tuple(vertical_gradient),
    )
