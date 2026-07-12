"""Conservative empirical thresholds in operational false alarms per month."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

SECONDS_PER_30_DAY_MONTH = 30.0 * 24.0 * 3600.0


@dataclass(frozen=True, slots=True)
class EmpiricalThreshold:
    threshold: float
    observed_exceedances: int
    noise_window_count: int
    window_step_s: float
    target_false_alarms_per_30_days: float
    observed_false_alarms_per_30_days: float
    minimum_nonzero_resolvable_false_alarms_per_30_days: float


@dataclass(frozen=True, slots=True)
class QuietScoreWindow:
    window_id: str
    split_role: str
    scores: tuple[float, ...]
    window_step_s: float

    def __post_init__(self) -> None:
        if not self.window_id.strip():
            raise ValueError("quiet score window ID must be non-empty")
        if self.split_role not in {"threshold_calibration", "held_out"}:
            raise ValueError("quiet score split role must be threshold_calibration or held_out")
        if not self.scores or not all(math.isfinite(value) for value in self.scores):
            raise ValueError("quiet scores must be non-empty and finite")
        if not math.isfinite(self.window_step_s) or self.window_step_s <= 0.0:
            raise ValueError("quiet score window step must be finite and positive")


@dataclass(frozen=True, slots=True)
class QuietWindowFalsePositiveAudit:
    threshold: EmpiricalThreshold
    calibration_window_ids: tuple[str, ...]
    heldout_window_ids: tuple[str, ...]
    heldout_score_count: int
    heldout_exceedance_count: int
    heldout_triggered_window_ids: tuple[str, ...]
    heldout_false_alarms_per_30_days: float
    heldout_minimum_nonzero_resolvable_false_alarms_per_30_days: float
    rate_resolution_sufficient: bool
    passes_target_rate: bool


def calibrate_empirical_threshold(
    noise_scores: Sequence[float],
    window_step_s: float,
    target_false_alarms_per_30_days: float,
) -> EmpiricalThreshold:
    """Choose the lowest observed-score threshold that does not exceed target FAR.

    When the record is too short to permit even one exceedance at the target
    rate, the threshold is placed just above the maximum observed noise score.
    Ties are handled conservatively.
    """

    if not noise_scores:
        raise ValueError("noise_scores must not be empty")
    scores = tuple(float(value) for value in noise_scores)
    if not all(math.isfinite(value) for value in scores):
        raise ValueError("noise scores must be finite")
    step = float(window_step_s)
    target = float(target_false_alarms_per_30_days)
    if not math.isfinite(step) or step <= 0.0:
        raise ValueError("window_step_s must be finite and positive")
    if not math.isfinite(target) or target < 0.0:
        raise ValueError("target false alarms must be finite and non-negative")

    windows_per_month = SECONDS_PER_30_DAY_MONTH / step
    allowed = math.floor(target / windows_per_month * len(scores))
    threshold = math.nextafter(max(scores), math.inf)
    exceedances = 0
    if allowed > 0:
        for candidate in sorted(set(scores)):
            candidate_exceedances = sum(score >= candidate for score in scores)
            if candidate_exceedances <= allowed:
                threshold = candidate
                exceedances = candidate_exceedances
                break
    observed_rate = exceedances / len(scores) * windows_per_month
    return EmpiricalThreshold(
        threshold=threshold,
        observed_exceedances=exceedances,
        noise_window_count=len(scores),
        window_step_s=step,
        target_false_alarms_per_30_days=target,
        observed_false_alarms_per_30_days=observed_rate,
        minimum_nonzero_resolvable_false_alarms_per_30_days=(
            windows_per_month / len(scores)
        ),
    )


def empirical_detection_probability(
    signal_scores: Sequence[float], threshold: float
) -> float:
    """Fraction of finite held-out signal scores meeting the frozen threshold."""

    if not signal_scores:
        raise ValueError("signal_scores must not be empty")
    scores = tuple(float(value) for value in signal_scores)
    threshold_value = float(threshold)
    if not all(math.isfinite(value) for value in scores) or not math.isfinite(
        threshold_value
    ):
        raise ValueError("signal scores and threshold must be finite")
    return sum(score >= threshold_value for score in scores) / len(scores)


def audit_quiet_window_false_positives(
    windows: Sequence[QuietScoreWindow],
    *,
    target_false_alarms_per_30_days: float,
) -> QuietWindowFalsePositiveAudit:
    """Freeze a threshold on calibration quiet windows and evaluate held-out quiets."""

    rows = tuple(windows)
    if len({row.window_id for row in rows}) != len(rows):
        raise ValueError("quiet score window IDs must be unique")
    calibration = tuple(row for row in rows if row.split_role == "threshold_calibration")
    heldout = tuple(row for row in rows if row.split_role == "held_out")
    if not calibration or not heldout:
        raise ValueError("quiet false-positive audit requires calibration and held-out windows")
    steps = {row.window_step_s for row in rows}
    if len(steps) != 1:
        raise ValueError("all quiet score windows must use the same decision step")
    step = next(iter(steps))
    threshold = calibrate_empirical_threshold(
        tuple(score for row in calibration for score in row.scores),
        step,
        target_false_alarms_per_30_days,
    )
    heldout_scores = tuple(score for row in heldout for score in row.scores)
    exceedance_count = sum(score >= threshold.threshold for score in heldout_scores)
    windows_per_month = SECONDS_PER_30_DAY_MONTH / step
    observed_rate = exceedance_count / len(heldout_scores) * windows_per_month
    triggered = tuple(
        sorted(
            row.window_id
            for row in heldout
            if any(score >= threshold.threshold for score in row.scores)
        )
    )
    target = float(target_false_alarms_per_30_days)
    minimum_nonzero_rate = windows_per_month / len(heldout_scores)
    resolution_sufficient = minimum_nonzero_rate <= target
    return QuietWindowFalsePositiveAudit(
        threshold=threshold,
        calibration_window_ids=tuple(sorted(row.window_id for row in calibration)),
        heldout_window_ids=tuple(sorted(row.window_id for row in heldout)),
        heldout_score_count=len(heldout_scores),
        heldout_exceedance_count=exceedance_count,
        heldout_triggered_window_ids=triggered,
        heldout_false_alarms_per_30_days=observed_rate,
        heldout_minimum_nonzero_resolvable_false_alarms_per_30_days=minimum_nonzero_rate,
        rate_resolution_sufficient=resolution_sufficient,
        passes_target_rate=resolution_sufficient and observed_rate <= target,
    )
