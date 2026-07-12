"""Provider-neutral interface for elastic-load Green-function responses."""

from __future__ import annotations

import math
from bisect import bisect_right
from collections.abc import Sequence
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class LoadGreenFunctionMetadata:
    """Provenance and normalization required for a load Green-function adapter."""

    provider_id: str
    provider_version: str
    earth_model: str
    source: str
    normalization: str = "per_source_mass_kg"
    component_semantics: str = "decomposed_deformation_and_internal_mass"

    def __post_init__(self) -> None:
        for name in ("provider_id", "provider_version", "earth_model", "source"):
            if not getattr(self, name).strip():
                raise ValueError(f"{name} must not be empty")
        if self.normalization != "per_source_mass_kg":
            raise ValueError("provider normalization must be 'per_source_mass_kg'")
        if self.component_semantics not in {
            "decomposed_deformation_and_internal_mass",
            "combined_elastic_gravity",
        }:
            raise ValueError("unsupported Green-function component semantics")


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


@dataclass(frozen=True, slots=True)
class CombinedElasticLoadGreenFunctionSample:
    """Combined elastic gravity when the source does not decompose its output."""

    elastic_gravity_m_s2_per_kg: float
    vertical_displacement_m_per_kg: float

    def __post_init__(self) -> None:
        if not all(
            math.isfinite(value)
            for value in (
                self.elastic_gravity_m_s2_per_kg,
                self.vertical_displacement_m_per_kg,
            )
        ):
            raise ValueError("combined Green-function response values must be finite")


@runtime_checkable
class LoadGreenFunctionProvider(Protocol):
    """Adapter protocol for a traceable, versioned load Green-function source."""

    metadata: LoadGreenFunctionMetadata

    def evaluate(self, angular_distance_rad: float) -> LoadGreenFunctionSample:
        """Return per-kilogram response at angular distance in radians."""


@dataclass(frozen=True, slots=True)
class TabulatedLoadGreenFunctionProvider:
    """No-extrapolation linear adapter for audited per-kilogram tables."""

    metadata: LoadGreenFunctionMetadata
    angular_distances_rad: tuple[float, ...]
    samples: tuple[LoadGreenFunctionSample, ...]
    interpolation: str = "linear_angular_distance"

    def __post_init__(self) -> None:
        if len(self.angular_distances_rad) != len(self.samples) or len(self.samples) < 2:
            raise ValueError("tabulated distances and samples must have equal length >= 2")
        if self.interpolation != "linear_angular_distance":
            raise ValueError("only linear_angular_distance interpolation is supported")
        if not all(
            math.isfinite(value) and 0.0 <= value <= math.pi
            for value in self.angular_distances_rad
        ):
            raise ValueError("tabulated angular distances must be finite and lie in [0, pi]")
        if any(
            self.angular_distances_rad[index + 1] <= self.angular_distances_rad[index]
            for index in range(len(self.angular_distances_rad) - 1)
        ):
            raise ValueError("tabulated angular distances must be strictly increasing")

    def evaluate(self, angular_distance_rad: float) -> LoadGreenFunctionSample:
        distance = float(angular_distance_rad)
        if not math.isfinite(distance):
            raise ValueError("angular_distance_rad must be finite")
        if distance < self.angular_distances_rad[0] or distance > self.angular_distances_rad[-1]:
            raise ValueError("refusing to extrapolate beyond the tabulated angular-distance range")
        index = bisect_right(self.angular_distances_rad, distance)
        if index == 0:
            return self.samples[0]
        if index == len(self.angular_distances_rad):
            return self.samples[-1]
        left = index - 1
        if distance == self.angular_distances_rad[left]:
            return self.samples[left]
        fraction = (distance - self.angular_distances_rad[left]) / (
            self.angular_distances_rad[index] - self.angular_distances_rad[left]
        )
        return LoadGreenFunctionSample(
            *(
                left_value + fraction * (right_value - left_value)
                for left_value, right_value in zip(
                    self.samples[left].as_tuple(), self.samples[index].as_tuple(), strict=True
                )
            )
        )

    @classmethod
    def from_json(cls, path: str | Path) -> "TabulatedLoadGreenFunctionProvider":
        """Load the project interchange format after explicit unit normalization."""

        document = json.loads(Path(path).read_text(encoding="utf-8"))
        if document.get("schema_version") != 1:
            raise ValueError("unsupported tabulated Green-function schema version")
        metadata = LoadGreenFunctionMetadata(**document["metadata"])
        distances = tuple(float(value) for value in document["angular_distances_rad"])
        component_names = (
            "deformation_gravity_m_s2_per_kg",
            "internal_mass_gravity_m_s2_per_kg",
            "vertical_displacement_m_per_kg",
        )
        components = [document[name] for name in component_names]
        if any(len(component) != len(distances) for component in components):
            raise ValueError("every tabulated component must match the distance array")
        samples = tuple(
            LoadGreenFunctionSample(*(float(component[index]) for component in components))
            for index in range(len(distances))
        )
        return cls(
            metadata=metadata,
            angular_distances_rad=distances,
            samples=samples,
            interpolation=document.get("interpolation", "linear_angular_distance"),
        )


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


@dataclass(frozen=True, slots=True)
class CombinedElasticLoadResponse:
    """Direct attraction plus an explicitly non-decomposed elastic response."""

    direct_attraction_m_s2: float
    combined_elastic_gravity_m_s2: float
    vertical_displacement_m: float
    green_function_provider_id: str
    green_function_provider_version: str
    earth_model: str

    def __post_init__(self) -> None:
        values = (
            self.direct_attraction_m_s2,
            self.combined_elastic_gravity_m_s2,
            self.vertical_displacement_m,
        )
        if not all(math.isfinite(value) for value in values):
            raise ValueError("combined load-response components must be finite")
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
        return math.fsum(
            (self.direct_attraction_m_s2, self.combined_elastic_gravity_m_s2)
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
    if provider.metadata.component_semantics != "decomposed_deformation_and_internal_mass":
        raise ValueError(
            "decomposed convolution requires decomposed Green-function semantics"
        )
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


def convolve_combined_elastic_load_green_functions(
    source_masses_kg: Sequence[float],
    angular_distances_rad: Sequence[float],
    provider: LoadGreenFunctionProvider,
    *,
    direct_attraction_m_s2: float,
) -> CombinedElasticLoadResponse:
    """Convolve a provider whose gravity output is explicitly not decomposed."""

    if len(source_masses_kg) != len(angular_distances_rad):
        raise ValueError("source-mass and angular-distance arrays must have equal length")
    if not isinstance(provider, LoadGreenFunctionProvider):
        raise TypeError("provider must satisfy LoadGreenFunctionProvider")
    if provider.metadata.component_semantics != "combined_elastic_gravity":
        raise ValueError(
            "combined convolution requires combined_elastic_gravity semantics"
        )
    direct = float(direct_attraction_m_s2)
    if not math.isfinite(direct):
        raise ValueError("direct_attraction_m_s2 must be finite")

    elastic_terms: list[float] = []
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
        if not isinstance(sample, CombinedElasticLoadGreenFunctionSample):
            raise TypeError(
                "combined provider must return CombinedElasticLoadGreenFunctionSample"
            )
        elastic_terms.append(mass * sample.elastic_gravity_m_s2_per_kg)
        displacement_terms.append(mass * sample.vertical_displacement_m_per_kg)

    metadata = provider.metadata
    return CombinedElasticLoadResponse(
        direct_attraction_m_s2=direct,
        combined_elastic_gravity_m_s2=math.fsum(elastic_terms),
        vertical_displacement_m=math.fsum(displacement_terms),
        green_function_provider_id=metadata.provider_id,
        green_function_provider_version=metadata.provider_version,
        earth_model=metadata.earth_model,
    )
