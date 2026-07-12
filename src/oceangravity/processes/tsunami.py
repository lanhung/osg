"""Mass-balanced propagating Gaussian crest-trough tsunami wave packet."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from oceangravity.constants import REFERENCE_SEAWATER_DENSITY, STANDARD_GRAVITY
from oceangravity.gravity import gaussian_surface_response_numerical

from .common import ScalarGravitySignal


@dataclass(frozen=True, slots=True)
class TsunamiWavePacketResult:
    signal: ScalarGravitySignal
    shallow_water_phase_speed_m_s: float
    crest_mass_amplitude_kg: float
    trough_mass_amplitude_kg: float

    @property
    def net_surface_mass_amplitude_kg(self) -> float:
        return math.fsum((self.crest_mass_amplitude_kg, self.trough_mass_amplitude_kg))


def propagating_compensated_gaussian_tsunami(
    times_s: Sequence[float],
    *,
    crest_peak_sea_level_m: float,
    horizontal_scale_m: float,
    crest_trough_separation_m: float,
    water_depth_m: float,
    crest_passage_time_s: float,
    wave_plane_z_m: float,
    observation_xyz_m: Sequence[float],
    water_density_kg_m3: float = REFERENCE_SEAWATER_DENSITY.value,
    radial_cells: int = 48,
    angular_cells: int = 72,
    cutoff_sigma: float = 8.0,
) -> TsunamiWavePacketResult:
    """Propagate equal/opposite Gaussian surface loads at shallow-water speed.

    Propagation is in local positive x. The negative trough trails the crest by the
    stated separation. Both Gaussians have equal integrated mass magnitude, so the
    idealized wave packet has zero net surface-water mass at every time.
    """

    times = tuple(float(value) for value in times_s)
    peak = float(crest_peak_sea_level_m)
    scale = float(horizontal_scale_m)
    separation = float(crest_trough_separation_m)
    depth = float(water_depth_m)
    passage_time = float(crest_passage_time_s)
    plane_z = float(wave_plane_z_m)
    density = float(water_density_kg_m3)
    observation = tuple(float(value) for value in observation_xyz_m)
    for name, value in (
        ("crest_peak_sea_level_m", peak),
        ("horizontal_scale_m", scale),
        ("crest_trough_separation_m", separation),
        ("water_depth_m", depth),
        ("crest_passage_time_s", passage_time),
        ("wave_plane_z_m", plane_z),
        ("water_density_kg_m3", density),
    ):
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")
    if len(observation) != 3 or not all(math.isfinite(value) for value in observation):
        raise ValueError("observation_xyz_m must contain three finite coordinates")
    if scale <= 0.0 or separation <= 0.0 or depth <= 0.0 or density <= 0.0:
        raise ValueError("scale, separation, depth, and density must be greater than zero")

    phase_speed = math.sqrt(STANDARD_GRAVITY.value * depth)
    local_sea_level = []
    vertical_gravity = []
    vertical_gradient = []
    peak_surface_density = density * peak
    for time in times:
        crest_x = phase_speed * (time - passage_time)
        trough_x = crest_x - separation
        crest_offset_squared = (
            (observation[0] - crest_x) ** 2 + observation[1] ** 2
        )
        trough_offset_squared = (
            (observation[0] - trough_x) ** 2 + observation[1] ** 2
        )
        local_sea_level.append(
            peak
            * (
                math.exp(-0.5 * crest_offset_squared / scale**2)
                - math.exp(-0.5 * trough_offset_squared / scale**2)
            )
        )
        crest_response = gaussian_surface_response_numerical(
            peak_surface_density,
            scale,
            (crest_x, 0.0, plane_z),
            observation,
            radial_cells=radial_cells,
            angular_cells=angular_cells,
            cutoff_sigma=cutoff_sigma,
        )
        trough_response = gaussian_surface_response_numerical(
            -peak_surface_density,
            scale,
            (trough_x, 0.0, plane_z),
            observation,
            radial_cells=radial_cells,
            angular_cells=angular_cells,
            cutoff_sigma=cutoff_sigma,
        )
        vertical_gravity.append(
            math.fsum(
                (crest_response.gravity_m_s2[2], trough_response.gravity_m_s2[2])
            )
        )
        vertical_gradient.append(
            math.fsum(
                (
                    crest_response.vertical_gravity_gradient_s2,
                    trough_response.vertical_gravity_gradient_s2,
                )
            )
        )

    mass_amplitude = 2.0 * math.pi * density * peak * scale**2
    signal = ScalarGravitySignal(
        process_id="propagating_compensated_gaussian_tsunami",
        times_s=times,
        source_amplitude=tuple(local_sea_level),
        source_amplitude_unit="m local crest-minus-trough sea-level anomaly",
        vertical_direct_gravity_m_s2=tuple(vertical_gravity),
        model_scope="direct attraction of a mass-balanced shallow-water Gaussian packet; no elastic/seismic source",
        vertical_direct_gravity_gradient_s2=tuple(vertical_gradient),
    )
    return TsunamiWavePacketResult(
        signal=signal,
        shallow_water_phase_speed_m_s=phase_speed,
        crest_mass_amplitude_kg=mass_amplitude,
        trough_mass_amplitude_kg=-mass_amplitude,
    )
