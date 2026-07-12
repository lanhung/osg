"""Explicit Gaussian reference thresholds for Paper 1 detectability comparisons."""

from __future__ import annotations

import math
from statistics import NormalDist

_STANDARD_NORMAL = NormalDist()


def gaussian_threshold_for_false_alarm(
    family_false_alarm_probability: float,
    *,
    independent_trials: int = 1,
) -> float:
    """Return a one-sided normalized-statistic threshold with a trials correction.

    The per-trial false-alarm probability is chosen so that the probability of at
    least one false alarm in ``independent_trials`` equals the requested family
    probability exactly under independent standard-normal trials.
    """

    probability = float(family_false_alarm_probability)
    if not math.isfinite(probability) or not 0.0 < probability < 1.0:
        raise ValueError("family_false_alarm_probability must lie in (0, 1)")
    if (
        isinstance(independent_trials, bool)
        or not isinstance(independent_trials, int)
        or independent_trials <= 0
    ):
        raise ValueError("independent_trials must be a positive integer")
    per_trial_probability = -math.expm1(math.log1p(-probability) / independent_trials)
    return _STANDARD_NORMAL.inv_cdf(1.0 - per_trial_probability)


def gaussian_detection_probability(expected_snr: float, threshold: float) -> float:
    """Return detection probability when statistic mean is expected SNR and variance is one."""

    snr = float(expected_snr)
    threshold_value = float(threshold)
    if not math.isfinite(snr) or snr < 0.0:
        raise ValueError("expected_snr must be finite and non-negative")
    if not math.isfinite(threshold_value):
        raise ValueError("threshold must be finite")
    return _STANDARD_NORMAL.cdf(snr - threshold_value)


def required_snr_for_detection_probability(
    threshold: float,
    target_detection_probability: float,
) -> float:
    """Invert the Gaussian reference model for required expected SNR."""

    threshold_value = float(threshold)
    probability = float(target_detection_probability)
    if not math.isfinite(threshold_value):
        raise ValueError("threshold must be finite")
    if not math.isfinite(probability) or not 0.0 < probability < 1.0:
        raise ValueError("target_detection_probability must lie in (0, 1)")
    return threshold_value + _STANDARD_NORMAL.inv_cdf(probability)

