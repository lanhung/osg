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
