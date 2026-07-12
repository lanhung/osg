"""Time-domain event attribution metrics with explicit masks and peak rules."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EventModelMetrics:
    included_sample_count: int
    bias_m_s2: float
    rmse_m_s2: float
    pearson_correlation: float | None
    explained_variance_fraction: float | None
    observed_peak_m_s2: float
    modeled_peak_m_s2: float
    peak_amplitude_error_m_s2: float
    observed_peak_time_s: float
    modeled_peak_time_s: float
    peak_time_error_s: float


def _mean(values: Sequence[float]) -> float:
    return math.fsum(values) / len(values)


def _population_variance(values: Sequence[float]) -> float:
    mean = _mean(values)
    return math.fsum((value - mean) ** 2 for value in values) / len(values)


def _signed_absolute_peak(values: Sequence[float]) -> tuple[int, float]:
    index = max(range(len(values)), key=lambda candidate: abs(values[candidate]))
    return index, values[index]


def evaluate_event_model_metrics(
    sample_times_s: Sequence[float],
    observed_m_s2: Sequence[float],
    modeled_m_s2: Sequence[float],
    *,
    inclusion_mask: Sequence[bool] | None = None,
) -> EventModelMetrics:
    """Compare model and observation using earliest signed absolute peaks."""

    times = tuple(float(value) for value in sample_times_s)
    observed = tuple(float(value) for value in observed_m_s2)
    modeled = tuple(float(value) for value in modeled_m_s2)
    if not times or not (len(times) == len(observed) == len(modeled)):
        raise ValueError("times, observed, and modeled series must have equal nonzero length")
    if not all(math.isfinite(value) for value in (*times, *observed, *modeled)):
        raise ValueError("event metric inputs must be finite")
    if any(times[index + 1] <= times[index] for index in range(len(times) - 1)):
        raise ValueError("event metric sample times must be strictly increasing")
    if inclusion_mask is None:
        mask = (True,) * len(times)
    else:
        mask = tuple(inclusion_mask)
        if len(mask) != len(times) or any(not isinstance(value, bool) for value in mask):
            raise ValueError("inclusion_mask must contain one boolean per sample")
    selected = [index for index, include in enumerate(mask) if include]
    if len(selected) < 2:
        raise ValueError("event metrics require at least two included samples")
    selected_times = tuple(times[index] for index in selected)
    selected_observed = tuple(observed[index] for index in selected)
    selected_modeled = tuple(modeled[index] for index in selected)

    residual = tuple(
        model - observation
        for observation, model in zip(selected_observed, selected_modeled, strict=True)
    )
    bias = _mean(residual)
    rmse = math.sqrt(math.fsum(value * value for value in residual) / len(residual))
    observed_mean = _mean(selected_observed)
    modeled_mean = _mean(selected_modeled)
    observed_sum_squares = math.fsum(
        (value - observed_mean) ** 2 for value in selected_observed
    )
    modeled_sum_squares = math.fsum(
        (value - modeled_mean) ** 2 for value in selected_modeled
    )
    correlation = None
    if observed_sum_squares > 0.0 and modeled_sum_squares > 0.0:
        covariance_sum = math.fsum(
            (observation - observed_mean) * (model - modeled_mean)
            for observation, model in zip(selected_observed, selected_modeled, strict=True)
        )
        correlation = covariance_sum / math.sqrt(
            observed_sum_squares * modeled_sum_squares
        )
        correlation = min(1.0, max(-1.0, correlation))
    observed_variance = _population_variance(selected_observed)
    explained_variance = None
    if observed_variance > 0.0:
        explained_variance = 1.0 - _population_variance(residual) / observed_variance

    observed_peak_index, observed_peak = _signed_absolute_peak(selected_observed)
    modeled_peak_index, modeled_peak = _signed_absolute_peak(selected_modeled)
    return EventModelMetrics(
        included_sample_count=len(selected),
        bias_m_s2=bias,
        rmse_m_s2=rmse,
        pearson_correlation=correlation,
        explained_variance_fraction=explained_variance,
        observed_peak_m_s2=observed_peak,
        modeled_peak_m_s2=modeled_peak,
        peak_amplitude_error_m_s2=modeled_peak - observed_peak,
        observed_peak_time_s=selected_times[observed_peak_index],
        modeled_peak_time_s=selected_times[modeled_peak_index],
        peak_time_error_s=(
            selected_times[modeled_peak_index] - selected_times[observed_peak_index]
        ),
    )
