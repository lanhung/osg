"""Oscillating compensated three-dimensional Gaussian density dipole."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from oceangravity.gravity import volume_cell_gravity, volume_cell_gravity_gradient

from .common import ScalarGravitySignal


@dataclass(frozen=True, slots=True)
class CompensatedDipoleResult:
    """Signal plus discrete mass/response diagnostics for a compensated dipole."""

    signal: ScalarGravitySignal
    positive_lobe_mass_per_unit_peak_density_m3: float
    negative_lobe_mass_per_unit_peak_density_m3: float
    unit_vertical_gravity_per_peak_density_m4_kg_s2: float
    unit_vertical_gradient_per_peak_density_m3_kg_s2: float
    grid_cells_per_lobe: int

    @property
    def net_mass_per_unit_peak_density_m3(self) -> float:
        return math.fsum(
            (
                self.positive_lobe_mass_per_unit_peak_density_m3,
                self.negative_lobe_mass_per_unit_peak_density_m3,
            )
        )


def oscillating_compensated_gaussian_dipole(
    times_s: Sequence[float],
    *,
    peak_density_anomaly_kg_m3: float,
    period_s: float,
    phase_rad: float,
    horizontal_scale_m: float,
    vertical_scale_m: float,
    lobe_separation_m: float,
    dipole_center_xyz_m: Sequence[float],
    observation_xyz_m: Sequence[float],
    cells_per_axis: int = 10,
    cutoff_sigma: float = 3.0,
) -> CompensatedDipoleResult:
    """Return direct gravity from two equal/opposite oscillating Gaussian lobes.

    Each lobe has the same discretized anisotropic Gaussian shape. Their centres
    are separated along local z. Unit density weights are exact sign copies, so
    their discrete signed mass cancels before the time-dependent amplitude is
    applied.
    """

    times = tuple(float(value) for value in times_s)
    peak_density = float(peak_density_anomaly_kg_m3)
    period = float(period_s)
    phase = float(phase_rad)
    horizontal_scale = float(horizontal_scale_m)
    vertical_scale = float(vertical_scale_m)
    separation = float(lobe_separation_m)
    cutoff = float(cutoff_sigma)
    center = tuple(float(value) for value in dipole_center_xyz_m)
    observation = tuple(float(value) for value in observation_xyz_m)
    for name, value in (
        ("peak_density_anomaly_kg_m3", peak_density),
        ("period_s", period),
        ("phase_rad", phase),
        ("horizontal_scale_m", horizontal_scale),
        ("vertical_scale_m", vertical_scale),
        ("lobe_separation_m", separation),
        ("cutoff_sigma", cutoff),
    ):
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")
    if len(center) != 3 or len(observation) != 3:
        raise ValueError("dipole centre and observation must contain three coordinates")
    if not all(math.isfinite(value) for value in center + observation):
        raise ValueError("dipole centre and observation coordinates must be finite")
    if period <= 0.0:
        raise ValueError("period_s must be greater than zero")
    if horizontal_scale <= 0.0 or vertical_scale <= 0.0:
        raise ValueError("horizontal_scale_m and vertical_scale_m must be greater than zero")
    if separation <= 0.0:
        raise ValueError("lobe_separation_m must be greater than zero")
    if cutoff <= 0.0:
        raise ValueError("cutoff_sigma must be greater than zero")
    if (
        isinstance(cells_per_axis, bool)
        or not isinstance(cells_per_axis, int)
        or cells_per_axis < 2
    ):
        raise ValueError("cells_per_axis must be an integer of at least two")

    step_horizontal = 2.0 * cutoff * horizontal_scale / cells_per_axis
    step_vertical = 2.0 * cutoff * vertical_scale / cells_per_axis
    local_x = tuple(
        -cutoff * horizontal_scale + (index + 0.5) * step_horizontal
        for index in range(cells_per_axis)
    )
    local_y = local_x
    local_z = tuple(
        -cutoff * vertical_scale + (index + 0.5) * step_vertical
        for index in range(cells_per_axis)
    )
    densities: list[float] = []
    cell_centers: list[tuple[float, float, float]] = []
    positive_weights: list[float] = []
    negative_weights: list[float] = []
    for sign, lobe_offset_z in ((1.0, 0.5 * separation), (-1.0, -0.5 * separation)):
        for x in local_x:
            for y in local_y:
                for z in local_z:
                    weight = math.exp(
                        -0.5
                        * (
                            (x / horizontal_scale) ** 2
                            + (y / horizontal_scale) ** 2
                            + (z / vertical_scale) ** 2
                        )
                    )
                    densities.append(sign * weight)
                    cell_centers.append(
                        (center[0] + x, center[1] + y, center[2] + lobe_offset_z + z)
                    )
                    (positive_weights if sign > 0.0 else negative_weights).append(sign * weight)

    cell_volume = step_horizontal**2 * step_vertical
    positive_mass_per_density = math.fsum(positive_weights) * cell_volume
    negative_mass_per_density = math.fsum(negative_weights) * cell_volume
    unit_gravity = volume_cell_gravity(
        densities,
        cell_centers,
        cell_volume,
        observation,
    )
    unit_gradient = volume_cell_gravity_gradient(
        densities,
        cell_centers,
        cell_volume,
        observation,
    )
    angular_frequency = 2.0 * math.pi / period
    density_amplitude = tuple(
        peak_density * math.cos(angular_frequency * time + phase) for time in times
    )
    signal = ScalarGravitySignal(
        process_id="oscillating_compensated_gaussian_density_dipole",
        times_s=times,
        source_amplitude=density_amplitude,
        source_amplitude_unit="kg m^-3 peak density anomaly in positive lobe",
        vertical_direct_gravity_m_s2=tuple(
            unit_gravity[2] * amplitude for amplitude in density_amplitude
        ),
        model_scope="direct attraction of equal/opposite 3-D Gaussian lobes; no free surface or elastic response",
        vertical_direct_gravity_gradient_s2=tuple(
            unit_gradient[2][2] * amplitude for amplitude in density_amplitude
        ),
    )
    return CompensatedDipoleResult(
        signal=signal,
        positive_lobe_mass_per_unit_peak_density_m3=positive_mass_per_density,
        negative_lobe_mass_per_unit_peak_density_m3=negative_mass_per_density,
        unit_vertical_gravity_per_peak_density_m4_kg_s2=unit_gravity[2],
        unit_vertical_gradient_per_peak_density_m3_kg_s2=unit_gradient[2][2],
        grid_cells_per_lobe=cells_per_axis**3,
    )
