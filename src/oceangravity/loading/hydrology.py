"""Transparent local-slab hydrology baselines for Paper 2 sensitivity tests."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from oceangravity.constants import GRAVITATIONAL_CONSTANT

from .gravity_budget import GravityCorrectionComponent


@dataclass(frozen=True, slots=True)
class DoubleExponentialHydrologyResult:
    timestamps_s: tuple[float, ...]
    precipitation_increment_m: tuple[float, ...]
    fast_storage_m: tuple[float, ...]
    slow_storage_m: tuple[float, ...]
    effective_water_height_m: tuple[float, ...]
    fast_time_constant_s: float
    slow_time_constant_s: float
    fast_fraction: float
    total_precipitation_m: float


def double_exponential_precipitation_storage(
    timestamps_s: Sequence[float],
    precipitation_increment_m: Sequence[float],
    *,
    fast_time_constant_s: float,
    slow_time_constant_s: float,
    fast_fraction: float,
    initial_fast_storage_m: float = 0.0,
    initial_slow_storage_m: float = 0.0,
) -> DoubleExponentialHydrologyResult:
    """Apply a causal weighted two-reservoir response to precipitation increments.

    ``precipitation_increment_m[i]`` is the accumulation assigned to timestamp
    ``timestamps_s[i]``. Existing storage first decays over the elapsed interval,
    then the new increment enters both linear reservoirs. Their outputs are mixed
    with explicit weights that sum to one, so one input increment is not counted
    twice in the effective storage.
    """

    timestamps = tuple(float(value) for value in timestamps_s)
    precipitation = tuple(float(value) for value in precipitation_increment_m)
    if not timestamps or len(timestamps) != len(precipitation):
        raise ValueError("timestamps and precipitation increments must match and be non-empty")
    if not all(math.isfinite(value) for value in (*timestamps, *precipitation)):
        raise ValueError("hydrology timestamps and precipitation must be finite")
    if any(timestamps[index + 1] <= timestamps[index] for index in range(len(timestamps) - 1)):
        raise ValueError("hydrology timestamps must be strictly increasing")
    if any(value < 0.0 for value in precipitation):
        raise ValueError("precipitation increments must be nonnegative")
    fast_tau = float(fast_time_constant_s)
    slow_tau = float(slow_time_constant_s)
    fraction = float(fast_fraction)
    initial_fast = float(initial_fast_storage_m)
    initial_slow = float(initial_slow_storage_m)
    if not all(
        math.isfinite(value)
        for value in (fast_tau, slow_tau, fraction, initial_fast, initial_slow)
    ):
        raise ValueError("hydrology response parameters must be finite")
    if fast_tau <= 0.0 or slow_tau <= fast_tau:
        raise ValueError("time constants must satisfy 0 < fast < slow")
    if not 0.0 <= fraction <= 1.0:
        raise ValueError("fast_fraction must lie in [0, 1]")
    if initial_fast < 0.0 or initial_slow < 0.0:
        raise ValueError("initial reservoir storages must be nonnegative")

    fast_state = initial_fast
    slow_state = initial_slow
    fast_storage = []
    slow_storage = []
    effective_storage = []
    for index, increment in enumerate(precipitation):
        if index > 0:
            elapsed = timestamps[index] - timestamps[index - 1]
            fast_state *= math.exp(-elapsed / fast_tau)
            slow_state *= math.exp(-elapsed / slow_tau)
        fast_state += increment
        slow_state += increment
        fast_storage.append(fast_state)
        slow_storage.append(slow_state)
        effective_storage.append(
            fraction * fast_state + (1.0 - fraction) * slow_state
        )
    return DoubleExponentialHydrologyResult(
        timestamps_s=timestamps,
        precipitation_increment_m=precipitation,
        fast_storage_m=tuple(fast_storage),
        slow_storage_m=tuple(slow_storage),
        effective_water_height_m=tuple(effective_storage),
        fast_time_constant_s=fast_tau,
        slow_time_constant_s=slow_tau,
        fast_fraction=fraction,
        total_precipitation_m=math.fsum(precipitation),
    )


def groundwater_level_to_equivalent_water_height(
    groundwater_level_change_m: Sequence[float],
    effective_porosity: float,
) -> tuple[float, ...]:
    """Convert water-table change to equivalent water height using porosity."""

    levels = tuple(float(value) for value in groundwater_level_change_m)
    porosity = float(effective_porosity)
    if not levels or not all(math.isfinite(value) for value in levels):
        raise ValueError("groundwater level changes must be non-empty and finite")
    if not math.isfinite(porosity) or not 0.0 <= porosity <= 1.0:
        raise ValueError("effective_porosity must lie in [0, 1]")
    return tuple(porosity * value for value in levels)


def water_equivalent_height_to_bouguer_slab_gravity(
    equivalent_water_height_m: Sequence[float],
    *,
    water_density_kg_m3: float = 1_000.0,
    load_below_observer: bool = True,
) -> tuple[float, ...]:
    """Return local-up gravity from an infinite water-equivalent slab.

    The magnitude is ``2 pi G rho h``. With the load below the observer, positive
    water storage attracts downward and therefore has a negative local-up
    component. This direct-attraction approximation excludes finite-domain and
    elastic-loading effects.
    """

    heights = tuple(float(value) for value in equivalent_water_height_m)
    density = float(water_density_kg_m3)
    if not heights or not all(math.isfinite(value) for value in heights):
        raise ValueError("equivalent water heights must be non-empty and finite")
    if not math.isfinite(density) or density <= 0.0:
        raise ValueError("water_density_kg_m3 must be finite and positive")
    if not isinstance(load_below_observer, bool):
        raise ValueError("load_below_observer must be boolean")
    direction = -1.0 if load_below_observer else 1.0
    factor = direction * 2.0 * math.pi * GRAVITATIONAL_CONSTANT.value * density
    return tuple(factor * height for height in heights)


def hydrology_bouguer_correction_component(
    equivalent_water_height_m: Sequence[float],
    *,
    component_id: str,
    source: str,
    water_density_kg_m3: float = 1_000.0,
    equivalent_height_standard_uncertainty_m: Sequence[float] | None = None,
    uncertainty_group_id: str | None = None,
) -> GravityCorrectionComponent:
    """Create a sign-audited local hydrology component for the gravity ledger."""

    gravity = water_equivalent_height_to_bouguer_slab_gravity(
        equivalent_water_height_m,
        water_density_kg_m3=water_density_kg_m3,
        load_below_observer=True,
    )
    uncertainty = None
    if equivalent_height_standard_uncertainty_m is not None:
        height_uncertainty = tuple(
            float(value) for value in equivalent_height_standard_uncertainty_m
        )
        if len(height_uncertainty) != len(gravity) or not all(
            math.isfinite(value) and value >= 0.0 for value in height_uncertainty
        ):
            raise ValueError(
                "equivalent-height standard uncertainty must match and be nonnegative"
            )
        factor = (
            2.0
            * math.pi
            * GRAVITATIONAL_CONSTANT.value
            * float(water_density_kg_m3)
        )
        uncertainty = tuple(factor * value for value in height_uncertainty)
    return GravityCorrectionComponent(
        component_id=component_id,
        values_m_s2=gravity,
        physical_effect_ids=("land_hydrology_direct_local_slab",),
        source=source,
        standard_uncertainty_m_s2=uncertainty,
        uncertainty_group_id=uncertainty_group_id,
    )
