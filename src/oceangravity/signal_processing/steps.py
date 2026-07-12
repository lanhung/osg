"""Explicit, reviewable instrument-step decisions without automatic estimation."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class InstrumentStepDecision:
    decision_id: str
    later_sample_index: int
    observed_step_m_s2: float
    source: str
    rationale: str

    def __post_init__(self) -> None:
        if not self.decision_id.strip() or not self.source.strip() or not self.rationale.strip():
            raise ValueError("step decision ID, source, and rationale must be non-empty")
        if isinstance(self.later_sample_index, bool) or not isinstance(
            self.later_sample_index, int
        ):
            raise ValueError("later_sample_index must be an integer")
        if not math.isfinite(self.observed_step_m_s2) or self.observed_step_m_s2 == 0.0:
            raise ValueError("observed step must be finite and nonzero")


@dataclass(frozen=True, slots=True)
class InstrumentStepCorrection:
    corrected_m_s2: tuple[float, ...]
    removed_cumulative_step_m_s2: tuple[float, ...]
    applied_decision_ids: tuple[str, ...]


def apply_instrument_step_decisions(
    values_m_s2: Sequence[float], decisions: Sequence[InstrumentStepDecision]
) -> InstrumentStepCorrection:
    """Subtract declared persistent steps from their later sample onward."""

    values = tuple(float(value) for value in values_m_s2)
    if not values or not all(math.isfinite(value) for value in values):
        raise ValueError("gravity values must be non-empty and finite")
    rows = tuple(decisions)
    identifiers = [row.decision_id for row in rows]
    indices = [row.later_sample_index for row in rows]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("step decision IDs must be unique")
    if len(set(indices)) != len(indices):
        raise ValueError("multiple step decisions at one sample are ambiguous")
    if any(index <= 0 or index >= len(values) for index in indices):
        raise ValueError("step later_sample_index must lie inside the series after index zero")
    ordered = tuple(sorted(rows, key=lambda row: row.later_sample_index))
    removed = []
    running = 0.0
    decision_by_index = {row.later_sample_index: row for row in ordered}
    for index in range(len(values)):
        if index in decision_by_index:
            running = math.fsum((running, decision_by_index[index].observed_step_m_s2))
        removed.append(running)
    corrected = tuple(
        value - correction for value, correction in zip(values, removed, strict=True)
    )
    return InstrumentStepCorrection(
        corrected_m_s2=corrected,
        removed_cumulative_step_m_s2=tuple(removed),
        applied_decision_ids=tuple(row.decision_id for row in ordered),
    )
