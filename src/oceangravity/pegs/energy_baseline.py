"""Leakage-safe single-station window-energy baseline for PEGS evaluation."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from oceangravity.evaluation.empirical_detection import (
    QuietScoreWindow,
    QuietWindowFalsePositiveAudit,
    audit_quiet_window_false_positives,
    empirical_detection_probability,
)


@dataclass(frozen=True, slots=True)
class WindowEnergyScores:
    scores: tuple[float, ...]
    start_sample_indices: tuple[int, ...]
    discarded_start_sample_indices: tuple[int, ...]
    window_length_samples: int
    decision_step_samples: int
    trailing_samples_after_last_start: int


@dataclass(frozen=True, slots=True)
class HeldoutEnergyEventResult:
    event_id: str
    score_count: int
    detection_probability: float
    earliest_trigger_index: int | None


@dataclass(frozen=True, slots=True)
class SingleStationEnergyAudit:
    quiet_false_positive_audit: QuietWindowFalsePositiveAudit
    heldout_events: tuple[HeldoutEnergyEventResult, ...]


def windowed_rms_energy_scores(
    samples: Sequence[float],
    *,
    window_length_samples: int,
    decision_step_samples: int,
    inclusion_mask: Sequence[bool] | None = None,
) -> WindowEnergyScores:
    """Return RMS scores for fully included windows in response-corrected units.

    RMS is the square root of mean squared amplitude. The function deliberately
    does not normalize by an estimated PSD; all compared windows must therefore
    share instrument response, units, passband, cadence, and preprocessing.
    """

    values = tuple(float(value) for value in samples)
    if not values or not all(math.isfinite(value) for value in values):
        raise ValueError("energy-baseline samples must be non-empty and finite")
    for name, value in (
        ("window_length_samples", window_length_samples),
        ("decision_step_samples", decision_step_samples),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"{name} must be a positive integer")
    if len(values) < window_length_samples:
        raise ValueError("sample record is shorter than one energy window")
    if inclusion_mask is None:
        mask = (True,) * len(values)
    else:
        mask = tuple(inclusion_mask)
        if len(mask) != len(values) or any(not isinstance(value, bool) for value in mask):
            raise ValueError("energy inclusion mask must contain one boolean per sample")

    starts = tuple(
        range(0, len(values) - window_length_samples + 1, decision_step_samples)
    )
    used = tuple(
        start
        for start in starts
        if all(mask[start : start + window_length_samples])
    )
    used_set = set(used)
    discarded = tuple(start for start in starts if start not in used_set)
    if not used:
        raise ValueError("energy baseline requires at least one fully included window")
    scores = tuple(
        math.sqrt(
            math.fsum(value * value for value in values[start : start + window_length_samples])
            / window_length_samples
        )
        for start in used
    )
    last_start = starts[-1]
    return WindowEnergyScores(
        scores=scores,
        start_sample_indices=used,
        discarded_start_sample_indices=discarded,
        window_length_samples=window_length_samples,
        decision_step_samples=decision_step_samples,
        trailing_samples_after_last_start=(
            len(values) - (last_start + window_length_samples)
        ),
    )


def audit_single_station_energy_baseline(
    quiet_windows: Sequence[QuietScoreWindow],
    heldout_event_scores: Mapping[str, Sequence[float]],
    *,
    target_false_alarms_per_30_days: float,
) -> SingleStationEnergyAudit:
    """Freeze a quiet threshold and apply it unchanged to held-out PEGS events."""

    quiet_rows = tuple(quiet_windows)
    audit = audit_quiet_window_false_positives(
        quiet_rows,
        target_false_alarms_per_30_days=target_false_alarms_per_30_days,
    )
    event_ids = tuple(sorted(heldout_event_scores))
    if not event_ids or any(not event_id.strip() for event_id in event_ids):
        raise ValueError("held-out event score mapping requires non-empty event IDs")
    quiet_ids = {row.window_id for row in quiet_rows}
    overlap = quiet_ids.intersection(event_ids)
    if overlap:
        raise ValueError(f"event and quiet window IDs overlap: {sorted(overlap)}")

    threshold = audit.threshold.threshold
    results = []
    for event_id in event_ids:
        scores = tuple(float(value) for value in heldout_event_scores[event_id])
        if not scores or not all(math.isfinite(value) for value in scores):
            raise ValueError("held-out event scores must be non-empty and finite")
        earliest = next(
            (index for index, score in enumerate(scores) if score >= threshold), None
        )
        results.append(
            HeldoutEnergyEventResult(
                event_id=event_id,
                score_count=len(scores),
                detection_probability=empirical_detection_probability(scores, threshold),
                earliest_trigger_index=earliest,
            )
        )
    return SingleStationEnergyAudit(audit, tuple(results))
