"""Time-dependent held-out detection metrics and reliable-decision timing."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DetectionProbabilityPoint:
    time_after_origin_s: float
    detected_events: int
    total_events: int
    detection_probability: float


def time_dependent_detection_probability(
    times_after_origin_s: Sequence[float],
    held_out_signal_scores: Sequence[Sequence[float]],
    threshold: float,
) -> tuple[DetectionProbabilityPoint, ...]:
    """Evaluate a frozen threshold over held-out events at every decision time."""

    times = tuple(float(value) for value in times_after_origin_s)
    if not times or not all(math.isfinite(value) and value >= 0.0 for value in times):
        raise ValueError("decision times must be non-empty, finite, and non-negative")
    if any(times[index + 1] <= times[index] for index in range(len(times) - 1)):
        raise ValueError("decision times must be strictly increasing")
    threshold_value = float(threshold)
    if not math.isfinite(threshold_value):
        raise ValueError("threshold must be finite")
    rows = tuple(tuple(float(value) for value in row) for row in held_out_signal_scores)
    if not rows or any(len(row) != len(times) for row in rows):
        raise ValueError("held-out score rows must be non-empty and match decision times")
    if not all(math.isfinite(value) for row in rows for value in row):
        raise ValueError("held-out signal scores must be finite")

    points = []
    for time_index, time in enumerate(times):
        detected = sum(row[time_index] >= threshold_value for row in rows)
        points.append(
            DetectionProbabilityPoint(
                time_after_origin_s=time,
                detected_events=detected,
                total_events=len(rows),
                detection_probability=detected / len(rows),
            )
        )
    return tuple(points)


def earliest_reliable_detection_time(
    points: Sequence[DetectionProbabilityPoint],
    minimum_detection_probability: float,
    *,
    required_consecutive_points: int = 1,
) -> float | None:
    """Return first threshold crossing sustained for the declared point count."""

    probability = float(minimum_detection_probability)
    if not math.isfinite(probability) or not 0.0 <= probability <= 1.0:
        raise ValueError("minimum_detection_probability must lie in [0, 1]")
    if (
        isinstance(required_consecutive_points, bool)
        or not isinstance(required_consecutive_points, int)
        or required_consecutive_points <= 0
    ):
        raise ValueError("required_consecutive_points must be a positive integer")
    if not points:
        raise ValueError("detection-probability points must not be empty")
    times = [point.time_after_origin_s for point in points]
    if any(times[index + 1] <= times[index] for index in range(len(times) - 1)):
        raise ValueError("detection-probability points must be strictly time ordered")
    for index in range(len(points) - required_consecutive_points + 1):
        window = points[index : index + required_consecutive_points]
        if all(point.detection_probability >= probability for point in window):
            return points[index].time_after_origin_s
    return None
