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


@dataclass(frozen=True, slots=True)
class GravityCorrectionStage:
    stage_index: int
    component_id: str
    input_m_s2: tuple[float, ...]
    removed_m_s2: tuple[float, ...]
    output_m_s2: tuple[float, ...]
    peak_absolute_removed_m_s2: float
    physical_effect_ids: tuple[str, ...]
    source: str


@dataclass(frozen=True, slots=True)
class GravityCorrectionChainResult:
    stages: tuple[GravityCorrectionStage, ...]
    final_residual: GravityResidualResult


@dataclass(frozen=True, slots=True)
class GravityCorrectionStageMetrics:
    stage_index: int
    component_id: str
    physical_effect_ids: tuple[str, ...]
    source: str
    input_mean_m_s2: float
    input_rms_m_s2: float
    removed_mean_m_s2: float
    removed_rms_m_s2: float
    peak_absolute_removed_m_s2: float
    output_mean_m_s2: float
    output_rms_m_s2: float
    stage_rms_change_fraction: float | None


@dataclass(frozen=True, slots=True)
class GravityCorrectionWaterfallMetrics:
    initial_rms_m_s2: float
    final_rms_m_s2: float
    total_rms_change_fraction: float | None
    closure_max_abs_m_s2: float
    stages: tuple[GravityCorrectionStageMetrics, ...]


def _mean(values: Sequence[float]) -> float:
    return math.fsum(values) / len(values)


def _rms(values: Sequence[float]) -> float:
    return math.sqrt(math.fsum(value * value for value in values) / len(values))


def _fractional_rms_change(before: float, after: float) -> float | None:
    return None if before == 0.0 else (before - after) / before


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


def apply_gravity_correction_chain(
    observed_m_s2: Sequence[float],
    ordered_components: Sequence[GravityCorrectionComponent],
) -> GravityCorrectionChainResult:
    """Apply a validated correction order while retaining every intermediate series."""

    final = compute_gravity_residual(observed_m_s2, ordered_components)
    current = final.observed_m_s2
    stages = []
    for index, component in enumerate(ordered_components, start=1):
        output = tuple(
            current[sample_index] - component.values_m_s2[sample_index]
            for sample_index in range(len(current))
        )
        stages.append(
            GravityCorrectionStage(
                stage_index=index,
                component_id=component.component_id,
                input_m_s2=current,
                removed_m_s2=component.values_m_s2,
                output_m_s2=output,
                peak_absolute_removed_m_s2=max(abs(value) for value in component.values_m_s2),
                physical_effect_ids=component.physical_effect_ids,
                source=component.source,
            )
        )
        current = output
    if current != final.residual_m_s2:
        difference = max(
            abs(left - right)
            for left, right in zip(current, final.residual_m_s2, strict=True)
        )
        if difference > max(final.closure_max_abs_m_s2, 1e-30) * 4.0:
            raise RuntimeError("sequential and direct correction paths do not close")
    return GravityCorrectionChainResult(stages=tuple(stages), final_residual=final)


def summarize_gravity_correction_waterfall(
    chain: GravityCorrectionChainResult,
) -> GravityCorrectionWaterfallMetrics:
    """Compute transparent stage metrics without changing correction series."""

    initial = chain.final_residual.observed_m_s2
    final = chain.final_residual.residual_m_s2
    initial_rms = _rms(initial)
    final_rms = _rms(final)
    stages = tuple(
        GravityCorrectionStageMetrics(
            stage_index=stage.stage_index,
            component_id=stage.component_id,
            physical_effect_ids=stage.physical_effect_ids,
            source=stage.source,
            input_mean_m_s2=_mean(stage.input_m_s2),
            input_rms_m_s2=_rms(stage.input_m_s2),
            removed_mean_m_s2=_mean(stage.removed_m_s2),
            removed_rms_m_s2=_rms(stage.removed_m_s2),
            peak_absolute_removed_m_s2=stage.peak_absolute_removed_m_s2,
            output_mean_m_s2=_mean(stage.output_m_s2),
            output_rms_m_s2=_rms(stage.output_m_s2),
            stage_rms_change_fraction=_fractional_rms_change(
                _rms(stage.input_m_s2), _rms(stage.output_m_s2)
            ),
        )
        for stage in chain.stages
    )
    return GravityCorrectionWaterfallMetrics(
        initial_rms_m_s2=initial_rms,
        final_rms_m_s2=final_rms,
        total_rms_change_fraction=_fractional_rms_change(initial_rms, final_rms),
        closure_max_abs_m_s2=chain.final_residual.closure_max_abs_m_s2,
        stages=stages,
    )
