"""Dependency-free, provisional conversion of audited LoadDef table columns."""

from __future__ import annotations

import math
from collections.abc import Sequence

from .green_functions import (
    CombinedElasticLoadGreenFunctionSample,
    LoadGreenFunctionMetadata,
    TabulatedCombinedElasticLoadGreenFunctionProvider,
)


def loaddef_normalized_elastic_gravity_to_si(
    normalized_gE: float,
    angular_distance_rad: float,
    earth_radius_m: float,
) -> float:
    """Reverse the documented `gE*(1e18*(a*theta))` output scaling.

    The caller must already have converted the table angle to radians. This
    utility is not scientific authorization: tag-specific equations, signs,
    source checksum and benchmark still pass through the separate audit gate.
    """

    value = float(normalized_gE)
    theta = float(angular_distance_rad)
    radius = float(earth_radius_m)
    if not math.isfinite(value):
        raise ValueError("normalized_gE must be finite")
    if not math.isfinite(theta) or not 0.0 < theta <= math.pi:
        raise ValueError("angular_distance_rad must lie in (0, pi]")
    if not math.isfinite(radius) or radius <= 0.0:
        raise ValueError("earth_radius_m must be finite and positive")
    return value / (1.0e18 * radius * theta)


def build_provisional_loaddef_combined_provider(
    *,
    metadata: LoadGreenFunctionMetadata,
    angular_distances: Sequence[float],
    angular_distance_unit: str,
    normalized_gE: Sequence[float],
    radial_displacement_m_per_kg: Sequence[float],
    earth_radius_m: float,
) -> TabulatedCombinedElasticLoadGreenFunctionProvider:
    """Build a no-extrapolation combined table from explicit LoadDef columns."""

    if metadata.component_semantics != "combined_elastic_gravity":
        raise ValueError("LoadDef provisional adapter requires combined semantics")
    if angular_distance_unit not in {"deg", "rad"}:
        raise ValueError("angular_distance_unit must be deg or rad")
    if not (
        len(angular_distances)
        == len(normalized_gE)
        == len(radial_displacement_m_per_kg)
    ):
        raise ValueError("LoadDef table columns must have equal length")
    angles_rad = tuple(
        math.radians(float(value)) if angular_distance_unit == "deg" else float(value)
        for value in angular_distances
    )
    samples = tuple(
        CombinedElasticLoadGreenFunctionSample(
            elastic_gravity_m_s2_per_kg=loaddef_normalized_elastic_gravity_to_si(
                normalized_gE[index], angle, earth_radius_m
            ),
            vertical_displacement_m_per_kg=float(radial_displacement_m_per_kg[index]),
        )
        for index, angle in enumerate(angles_rad)
    )
    return TabulatedCombinedElasticLoadGreenFunctionProvider(
        metadata=metadata,
        angular_distances_rad=angles_rad,
        samples=samples,
    )
