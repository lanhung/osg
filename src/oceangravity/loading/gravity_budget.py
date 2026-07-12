"""Auditable gravity residual assembly with physical-effect collision checks."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GravityCorrectionComponent:
    """One modeled series subtracted from observation with declared effects."""

    component_id: str
    values_m_s2: tuple[float, ...]
    physical_effect_ids: tuple[str, ...]
    source: str
    preapplied_to_input: bool = False

    def __post_init__(self) -> None:
        if not self.component_id.strip() or not self.source.strip():
            raise ValueError("component ID and source must not be empty")
        if not self.values_m_s2 or not all(math.isfinite(value) for value in self.values_m_s2):
            raise ValueError("component values must be non-empty and finite")
        if not self.physical_effect_ids or any(
            not effect.strip() for effect in self.physical_effect_ids
        ):
            raise ValueError("physical effect IDs must be non-empty")
        if len(set(self.physical_effect_ids)) != len(self.physical_effect_ids):
            raise ValueError("physical effect IDs must be unique within a component")


@dataclass(frozen=True, slots=True)
class GravityResidualResult:
    residual_m_s2: tuple[float, ...]
    observed_m_s2: tuple[float, ...]
    subtracted_component_ids: tuple[str, ...]
    closure_max_abs_m_s2: float


def compute_gravity_residual(
    observed_m_s2: Sequence[float],
    components: Sequence[GravityCorrectionComponent],
) -> GravityResidualResult:
    """Subtract non-overlapping components and verify sample-wise closure."""

    observed = tuple(float(value) for value in observed_m_s2)
    if not observed or not all(math.isfinite(value) for value in observed):
        raise ValueError("observed gravity must be non-empty and finite")
    component_ids = [component.component_id for component in components]
    if len(set(component_ids)) != len(component_ids):
        raise ValueError("gravity correction component IDs must be unique")
    effect_owner: dict[str, str] = {}
    for component in components:
        if component.preapplied_to_input:
            raise ValueError(
                f"component {component.component_id!r} is already applied to the input"
            )
        if len(component.values_m_s2) != len(observed):
            raise ValueError("every correction component must match observation length")
        for effect in component.physical_effect_ids:
            if effect in effect_owner:
                raise ValueError(
                    f"physical effect {effect!r} occurs in both "
                    f"{effect_owner[effect]!r} and {component.component_id!r}"
                )
            effect_owner[effect] = component.component_id

    residual = tuple(
        observed[index]
        - math.fsum(component.values_m_s2[index] for component in components)
        for index in range(len(observed))
    )
    closure = max(
        abs(
            observed[index]
            - math.fsum(
                (
                    residual[index],
                    *(component.values_m_s2[index] for component in components),
                )
            )
        )
        for index in range(len(observed))
    )
    return GravityResidualResult(
        residual_m_s2=residual,
        observed_m_s2=observed,
        subtracted_component_ids=tuple(component_ids),
        closure_max_abs_m_s2=closure,
    )
