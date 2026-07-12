"""Transparent local-slab hydrology baselines for Paper 2 sensitivity tests."""

from __future__ import annotations

import math
from collections.abc import Sequence

from oceangravity.constants import GRAVITATIONAL_CONSTANT


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
