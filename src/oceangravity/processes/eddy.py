"""Translating Gaussian sea-surface expression of a mesoscale eddy."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from oceangravity.constants import REFERENCE_SEAWATER_DENSITY
from oceangravity.gravity import (
    gaussian_surface_response_numerical,
    volume_cell_gravity,
    volume_cell_gravity_gradient,
)

from .common import ScalarGravitySignal


@dataclass(frozen=True, slots=True)
class CompensatedDensityEddyResult:
    signal: ScalarGravitySignal
    positive_mass_per_unit_core_density_m3: float
    negative_mass_per_unit_core_density_m3: float
    halo_density_scale_relative_to_core: float
    grid_cells: int

    @property
    def net_mass_per_unit_core_density_m3(self) -> float:
        return math.fsum(
            (
                self.positive_mass_per_unit_core_density_m3,
                self.negative_mass_per_unit_core_density_m3,
            )
        )


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


def translating_compensated_gaussian_density_eddy(
    times_s: Sequence[float],
    *,
    peak_core_density_anomaly_kg_m3: float,
    core_horizontal_scale_m: float,
    halo_horizontal_scale_m: float,
    vertical_scale_m: float,
    translation_speed_x_m_s: float,
    closest_approach_y_m: float,
    passage_time_s: float,
    center_z_m: float,
    observation_xyz_m: Sequence[float],
    cells_per_axis: int = 8,
    cutoff_sigma: float = 3.0,
) -> CompensatedDensityEddyResult:
    """Translate an exactly mass-balanced positive core and negative broad halo."""

    times = tuple(float(value) for value in times_s)
    peak = float(peak_core_density_anomaly_kg_m3)
    core_scale = float(core_horizontal_scale_m)
    halo_scale = float(halo_horizontal_scale_m)
    vertical_scale = float(vertical_scale_m)
    speed = float(translation_speed_x_m_s)
    closest_y = float(closest_approach_y_m)
    passage_time = float(passage_time_s)
    center_z = float(center_z_m)
    cutoff = float(cutoff_sigma)
    observation = tuple(float(value) for value in observation_xyz_m)
    scalars = (
        peak,
        core_scale,
        halo_scale,
        vertical_scale,
        speed,
        closest_y,
        passage_time,
        center_z,
        cutoff,
    )
    if not all(math.isfinite(value) for value in scalars):
        raise ValueError("eddy density parameters must be finite")
    if len(observation) != 3 or not all(math.isfinite(value) for value in observation):
        raise ValueError("observation_xyz_m must contain three finite coordinates")
    if core_scale <= 0.0 or halo_scale <= core_scale or vertical_scale <= 0.0:
        raise ValueError("scales must be positive and halo scale must exceed core scale")
    if speed == 0.0:
        raise ValueError("translation_speed_x_m_s must be nonzero")
    if cutoff <= 0.0:
        raise ValueError("cutoff_sigma must be positive")
    if (
        isinstance(cells_per_axis, bool)
        or not isinstance(cells_per_axis, int)
        or cells_per_axis < 2
    ):
        raise ValueError("cells_per_axis must be an integer of at least two")

    def gaussian_cells(horizontal_scale: float) -> tuple[list[tuple[float, float, float]], list[float], float]:
        horizontal_step = 2.0 * cutoff * horizontal_scale / cells_per_axis
        vertical_step = 2.0 * cutoff * vertical_scale / cells_per_axis
        horizontal = [
            -cutoff * horizontal_scale + (index + 0.5) * horizontal_step
            for index in range(cells_per_axis)
        ]
        vertical = [
            -cutoff * vertical_scale + (index + 0.5) * vertical_step
            for index in range(cells_per_axis)
        ]
        centers = []
        weights = []
        for x in horizontal:
            for y in horizontal:
                for z in vertical:
                    centers.append((x, y, z))
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
        return centers, weights, horizontal_step**2 * vertical_step

    core_centers, core_weights, core_volume = gaussian_cells(core_scale)
    halo_centers, halo_weights, halo_volume = gaussian_cells(halo_scale)
    core_mass_per_density = math.fsum(core_weights) * core_volume
    unscaled_halo_mass_per_density = math.fsum(halo_weights) * halo_volume
    halo_density_scale = core_mass_per_density / unscaled_halo_mass_per_density
    unit_densities = tuple(core_weights) + tuple(
        -halo_density_scale * weight for weight in halo_weights
    )
    cell_volumes = (core_volume,) * len(core_weights) + (halo_volume,) * len(halo_weights)
    local_centers = tuple(core_centers) + tuple(halo_centers)

    source_amplitude = []
    vertical_gravity = []
    vertical_gradient = []
    for time in times:
        center_x = speed * (time - passage_time)
        centers = tuple(
            (center_x + x, closest_y + y, center_z + z) for x, y, z in local_centers
        )
        gravity = volume_cell_gravity(
            unit_densities, cell_centers_xyz_m=centers, cell_volumes_m3=cell_volumes,
            observation_xyz_m=observation,
        )
        gradient = volume_cell_gravity_gradient(
            unit_densities, cell_centers_xyz_m=centers, cell_volumes_m3=cell_volumes,
            observation_xyz_m=observation,
        )
        horizontal_offset_squared = (
            (observation[0] - center_x) ** 2 + (observation[1] - closest_y) ** 2
        )
        source_amplitude.append(
            peak * math.exp(-0.5 * horizontal_offset_squared / core_scale**2)
        )
        vertical_gravity.append(peak * gravity[2])
        vertical_gradient.append(peak * gradient[2][2])

    signal = ScalarGravitySignal(
        process_id="translating_compensated_gaussian_density_eddy",
        times_s=times,
        source_amplitude=tuple(source_amplitude),
        source_amplitude_unit="kg m^-3 local positive-core density anomaly",
        vertical_direct_gravity_m_s2=tuple(vertical_gravity),
        model_scope="direct attraction of exactly compensated 3-D Gaussian core/halo; no free surface or elastic response",
        vertical_direct_gravity_gradient_s2=tuple(vertical_gradient),
    )
    return CompensatedDensityEddyResult(
        signal=signal,
        positive_mass_per_unit_core_density_m3=core_mass_per_density,
        negative_mass_per_unit_core_density_m3=(
            -halo_density_scale * unscaled_halo_mass_per_density
        ),
        halo_density_scale_relative_to_core=halo_density_scale,
        grid_cells=len(unit_densities),
    )
