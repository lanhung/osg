"""Leakage-safe linear ocean attribution fit across declared training events."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OceanAttributionFit:
    intercept_m_s2: float
    ocean_coefficient: float
    ocean_coefficient_standard_error: float
    residual_rmse_m_s2: float
    included_sample_count: int
    training_event_ids: tuple[str, ...]


def fit_ocean_attribution_coefficient(
    observed_m_s2: Sequence[float],
    baseline_prediction_m_s2: Sequence[float],
    ocean_prediction_m_s2: Sequence[float],
    event_id_by_sample: Sequence[str],
    *,
    training_event_ids: Sequence[str],
    inclusion_mask: Sequence[bool] | None = None,
) -> OceanAttributionFit:
    """Fit residual-on-ocean OLS using only declared training-event samples."""

    observed = tuple(float(value) for value in observed_m_s2)
    baseline = tuple(float(value) for value in baseline_prediction_m_s2)
    ocean = tuple(float(value) for value in ocean_prediction_m_s2)
    event_ids = tuple(event_id_by_sample)
    if not observed or not (
        len(observed) == len(baseline) == len(ocean) == len(event_ids)
    ):
        raise ValueError("attribution arrays must have equal nonzero length")
    if not all(math.isfinite(value) for value in (*observed, *baseline, *ocean)):
        raise ValueError("attribution numeric inputs must be finite")
    if any(not isinstance(event_id, str) or not event_id.strip() for event_id in event_ids):
        raise ValueError("every attribution sample requires a non-empty event ID")
    training = tuple(sorted(set(training_event_ids)))
    if not training or any(not isinstance(event_id, str) or not event_id.strip() for event_id in training):
        raise ValueError("training_event_ids must contain non-empty event IDs")
    unknown_training = set(training) - set(event_ids)
    if unknown_training:
        raise ValueError(f"training events have no samples: {sorted(unknown_training)}")
    if inclusion_mask is None:
        mask = (True,) * len(observed)
    else:
        mask = tuple(inclusion_mask)
        if len(mask) != len(observed) or any(not isinstance(value, bool) for value in mask):
            raise ValueError("attribution inclusion mask must contain one boolean per sample")
    selected = [
        index
        for index, event_id in enumerate(event_ids)
        if mask[index] and event_id in set(training)
    ]
    if len(selected) < 3:
        raise ValueError("attribution OLS requires at least three included training samples")
    x = tuple(ocean[index] for index in selected)
    y = tuple(observed[index] - baseline[index] for index in selected)
    x_mean = math.fsum(x) / len(x)
    y_mean = math.fsum(y) / len(y)
    x_sum_squares = math.fsum((value - x_mean) ** 2 for value in x)
    if x_sum_squares == 0.0:
        raise ValueError("ocean predictor has zero variance in training samples")
    cross_sum = math.fsum(
        (x_value - x_mean) * (y_value - y_mean)
        for x_value, y_value in zip(x, y, strict=True)
    )
    coefficient = cross_sum / x_sum_squares
    intercept = y_mean - coefficient * x_mean
    residuals = tuple(
        y_value - intercept - coefficient * x_value
        for x_value, y_value in zip(x, y, strict=True)
    )
    residual_sum_squares = math.fsum(value * value for value in residuals)
    residual_variance = residual_sum_squares / (len(x) - 2)
    standard_error = math.sqrt(residual_variance / x_sum_squares)
    return OceanAttributionFit(
        intercept_m_s2=intercept,
        ocean_coefficient=coefficient,
        ocean_coefficient_standard_error=standard_error,
        residual_rmse_m_s2=math.sqrt(residual_sum_squares / len(x)),
        included_sample_count=len(x),
        training_event_ids=training,
    )


def predict_heldout_ocean_attribution(
    fit: OceanAttributionFit,
    baseline_prediction_m_s2: Sequence[float],
    ocean_prediction_m_s2: Sequence[float],
    *,
    event_id: str,
) -> tuple[float, ...]:
    """Predict one event and reject any event used by the fit."""

    if not event_id.strip():
        raise ValueError("held-out event ID must be non-empty")
    if event_id in fit.training_event_ids:
        raise ValueError("event is not held out; it was used by the attribution fit")
    baseline = tuple(float(value) for value in baseline_prediction_m_s2)
    ocean = tuple(float(value) for value in ocean_prediction_m_s2)
    if not baseline or len(baseline) != len(ocean):
        raise ValueError("held-out baseline and ocean predictions must match and be non-empty")
    if not all(math.isfinite(value) for value in (*baseline, *ocean)):
        raise ValueError("held-out predictions must be finite")
    return tuple(
        baseline_value + fit.intercept_m_s2 + fit.ocean_coefficient * ocean_value
        for baseline_value, ocean_value in zip(baseline, ocean, strict=True)
    )
