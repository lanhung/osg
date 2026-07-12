"""Provider-neutral interface for elastic-load Green-function responses."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class LoadGreenFunctionMetadata:
    """Provenance and normalization required for a load Green-function adapter."""

    provider_id: str
    provider_version: str
    earth_model: str
    source: str
    normalization: str = "per_source_mass_kg"

    def __post_init__(self) -> None:
        for name in ("provider_id", "provider_version", "earth_model", "source"):
            if not getattr(self, name).strip():
                raise ValueError(f"{name} must not be empty")
        if self.normalization != "per_source_mass_kg":
            raise ValueError("provider normalization must be 'per_source_mass_kg'")


@dataclass(frozen=True, slots=True)
class LoadGreenFunctionSample:
    """Elastic-Earth response to one kilogram at an angular separation."""

    deformation_gravity_m_s2_per_kg: float
    internal_mass_gravity_m_s2_per_kg: float
    vertical_displacement_m_per_kg: float

    def __post_init__(self) -> None:
        if not all(math.isfinite(value) for value in self.as_tuple()):
            raise ValueError("Green-function response values must be finite")

    def as_tuple(self) -> tuple[float, float, float]:
        return (
            self.deformation_gravity_m_s2_per_kg,
            self.internal_mass_gravity_m_s2_per_kg,
            self.vertical_displacement_m_per_kg,
        )


@runtime_checkable
class LoadGreenFunctionProvider(Protocol):
    """Adapter protocol for a traceable, versioned load Green-function source."""

    metadata: LoadGreenFunctionMetadata

    def evaluate(self, angular_distance_rad: float) -> LoadGreenFunctionSample:
        """Return per-kilogram response at angular distance in radians."""


@dataclass(frozen=True, slots=True)
class LoadResponseComponents:
    """Separated direct and elastic components for one observation."""

    direct_attraction_m_s2: float
    deformation_gravity_m_s2: float
    internal_mass_gravity_m_s2: float
    vertical_displacement_m: float
    green_function_provider_id: str
    green_function_provider_version: str
    earth_model: str

    def __post_init__(self) -> None:
        values = (
            self.direct_attraction_m_s2,
            self.deformation_gravity_m_s2,
            self.internal_mass_gravity_m_s2,
            self.vertical_displacement_m,
        )
        if not all(math.isfinite(value) for value in values):
            raise ValueError("load-response components must be finite")
        if not all(
            value.strip()
            for value in (
                self.green_function_provider_id,
                self.green_function_provider_version,
                self.earth_model,
            )
        ):
            raise ValueError("load-response provider metadata must not be empty")

    @property
    def total_gravity_m_s2(self) -> float:
        """Return the documented sum of the three gravity contributions."""

        return math.fsum(
            (
                self.direct_attraction_m_s2,
                self.deformation_gravity_m_s2,
                self.internal_mass_gravity_m_s2,
            )
        )


def convolve_load_green_functions(
    source_masses_kg: Sequence[float],
    angular_distances_rad: Sequence[float],
    provider: LoadGreenFunctionProvider,
    *,
    direct_attraction_m_s2: float,
) -> LoadResponseComponents:
    """Convolve point-load masses while preserving each physical component.

    Direct attraction is a required explicit input because an elastic provider must
    not silently add or omit it. The caller computes that term with the documented
    source/observer geometry.
    """

    if len(source_masses_kg) != len(angular_distances_rad):
        raise ValueError("source-mass and angular-distance arrays must have equal length")
    if not isinstance(provider, LoadGreenFunctionProvider):
        raise TypeError("provider must satisfy LoadGreenFunctionProvider")
    direct = float(direct_attraction_m_s2)
    if not math.isfinite(direct):
        raise ValueError("direct_attraction_m_s2 must be finite")

    deformation_terms: list[float] = []
    internal_terms: list[float] = []
    displacement_terms: list[float] = []
    for index, (raw_mass, raw_distance) in enumerate(
        zip(source_masses_kg, angular_distances_rad, strict=True)
    ):
        mass = float(raw_mass)
        distance = float(raw_distance)
        if not math.isfinite(mass):
            raise ValueError(f"source mass at index {index} must be finite")
        if not math.isfinite(distance) or not 0.0 <= distance <= math.pi:
            raise ValueError(f"angular distance at index {index} must lie in [0, pi]")
        if mass == 0.0:
            continue
        sample = provider.evaluate(distance)
        deformation_terms.append(mass * sample.deformation_gravity_m_s2_per_kg)
        internal_terms.append(mass * sample.internal_mass_gravity_m_s2_per_kg)
        displacement_terms.append(mass * sample.vertical_displacement_m_per_kg)

    metadata = provider.metadata
    return LoadResponseComponents(
        direct_attraction_m_s2=direct,
        deformation_gravity_m_s2=math.fsum(deformation_terms),
        internal_mass_gravity_m_s2=math.fsum(internal_terms),
        vertical_displacement_m=math.fsum(displacement_terms),
        green_function_provider_id=metadata.provider_id,
        green_function_provider_version=metadata.provider_version,
        earth_model=metadata.earth_model,
    )

