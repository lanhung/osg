"""Time-dependent held-out magnitude and high-risk classification metrics."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MagnitudePerformancePoint:
    time_after_origin_s: float
    event_count: int
    mean_absolute_error: float
    mean_error_bias: float
    high_risk_sensitivity: float | None
    low_risk_specificity: float | None
    interval_coverage_probability: float | None


def time_dependent_magnitude_performance(
    times_after_origin_s: Sequence[float],
    true_magnitudes: Sequence[float],
    predicted_magnitudes: Sequence[Sequence[float]],
    *,
    high_risk_magnitude: float = 8.2,
    lower_intervals: Sequence[Sequence[float]] | None = None,
    upper_intervals: Sequence[Sequence[float]] | None = None,
) -> tuple[MagnitudePerformancePoint, ...]:
    """Compute held-out regression, risk classification, and interval coverage."""

    times = tuple(float(value) for value in times_after_origin_s)
    truth = tuple(float(value) for value in true_magnitudes)
    predictions = tuple(tuple(float(value) for value in row) for row in predicted_magnitudes)
    if not times or any(not math.isfinite(value) or value < 0.0 for value in times):
        raise ValueError("times must be non-empty, finite, and non-negative")
    if any(times[index + 1] <= times[index] for index in range(len(times) - 1)):
        raise ValueError("times must be strictly increasing")
    if not truth or len(predictions) != len(truth):
        raise ValueError("truth and prediction rows must have equal nonzero event count")
    if any(len(row) != len(times) for row in predictions):
        raise ValueError("every prediction row must match the time axis")
    if not all(math.isfinite(value) for value in truth) or not all(
        math.isfinite(value) for row in predictions for value in row
    ):
        raise ValueError("magnitudes must be finite")
    risk_threshold = float(high_risk_magnitude)
    if not math.isfinite(risk_threshold):
        raise ValueError("high-risk magnitude threshold must be finite")

    if (lower_intervals is None) != (upper_intervals is None):
        raise ValueError("lower and upper intervals must be supplied together")
    lower = upper = None
    if lower_intervals is not None and upper_intervals is not None:
        lower = tuple(tuple(float(value) for value in row) for row in lower_intervals)
        upper = tuple(tuple(float(value) for value in row) for row in upper_intervals)
        if len(lower) != len(truth) or len(upper) != len(truth):
            raise ValueError("interval rows must match event count")
        if any(len(row) != len(times) for row in lower + upper):
            raise ValueError("interval rows must match the time axis")
        if not all(math.isfinite(value) for row in lower + upper for value in row):
            raise ValueError("interval bounds must be finite")
        if any(
            lower[event][time] > upper[event][time]
            for event in range(len(truth))
            for time in range(len(times))
        ):
            raise ValueError("lower interval bounds cannot exceed upper bounds")

    points = []
    positive_count = sum(value >= risk_threshold for value in truth)
    negative_count = len(truth) - positive_count
    for time_index, time in enumerate(times):
        errors = [predictions[event][time_index] - truth[event] for event in range(len(truth))]
        true_positives = sum(
            truth[event] >= risk_threshold
            and predictions[event][time_index] >= risk_threshold
            for event in range(len(truth))
        )
        true_negatives = sum(
            truth[event] < risk_threshold
            and predictions[event][time_index] < risk_threshold
            for event in range(len(truth))
        )
        coverage = None
        if lower is not None and upper is not None:
            coverage = sum(
                lower[event][time_index] <= truth[event] <= upper[event][time_index]
                for event in range(len(truth))
            ) / len(truth)
        points.append(
            MagnitudePerformancePoint(
                time_after_origin_s=time,
                event_count=len(truth),
                mean_absolute_error=math.fsum(abs(error) for error in errors) / len(errors),
                mean_error_bias=math.fsum(errors) / len(errors),
                high_risk_sensitivity=(
                    true_positives / positive_count if positive_count else None
                ),
                low_risk_specificity=(
                    true_negatives / negative_count if negative_count else None
                ),
                interval_coverage_probability=coverage,
            )
        )
    return tuple(points)


def earliest_reliable_magnitude_time(
    points: Sequence[MagnitudePerformancePoint],
    *,
    maximum_mae: float,
    minimum_high_risk_sensitivity: float,
    minimum_low_risk_specificity: float,
    minimum_interval_coverage: float | None = None,
    required_consecutive_points: int = 1,
) -> float | None:
    """Return first sustained time satisfying every declared magnitude criterion."""

    limits = (
        float(maximum_mae),
        float(minimum_high_risk_sensitivity),
        float(minimum_low_risk_specificity),
    )
    if not math.isfinite(limits[0]) or limits[0] < 0.0:
        raise ValueError("maximum_mae must be finite and non-negative")
    if any(not math.isfinite(value) or not 0.0 <= value <= 1.0 for value in limits[1:]):
        raise ValueError("sensitivity and specificity minima must lie in [0, 1]")
    coverage_minimum = None if minimum_interval_coverage is None else float(minimum_interval_coverage)
    if coverage_minimum is not None and (
        not math.isfinite(coverage_minimum) or not 0.0 <= coverage_minimum <= 1.0
    ):
        raise ValueError("minimum interval coverage must lie in [0, 1]")
    if (
        isinstance(required_consecutive_points, bool)
        or not isinstance(required_consecutive_points, int)
        or required_consecutive_points <= 0
    ):
        raise ValueError("required_consecutive_points must be a positive integer")
    if not points:
        raise ValueError("magnitude points must not be empty")

    def qualifies(point: MagnitudePerformancePoint) -> bool:
        if point.high_risk_sensitivity is None or point.low_risk_specificity is None:
            return False
        if point.mean_absolute_error > limits[0]:
            return False
        if point.high_risk_sensitivity < limits[1] or point.low_risk_specificity < limits[2]:
            return False
        return coverage_minimum is None or (
            point.interval_coverage_probability is not None
            and point.interval_coverage_probability >= coverage_minimum
        )

    for index in range(len(points) - required_consecutive_points + 1):
        if all(qualifies(point) for point in points[index : index + required_consecutive_points]):
            return points[index].time_after_origin_s
    return None
