"""Transparent time-series quality summaries without automatic correction."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from .timebase import TimebaseSegmentationResult, split_uniform_time_series


@dataclass(frozen=True, slots=True)
class TimeSeriesQualitySummary:
    timebase: TimebaseSegmentationResult
    discontinuity_threshold: float
    discontinuity_later_indices: tuple[int, ...]
    maximum_finite_adjacent_difference: float

    @property
    def discontinuity_count(self) -> int:
        return len(self.discontinuity_later_indices)

    @property
    def missing_fraction(self) -> float:
        return self.timebase.missing_samples / self.timebase.input_samples


def assess_time_series_quality(
    timestamps_s: Sequence[float],
    samples: Sequence[float | None],
    expected_interval_s: float,
    *,
    discontinuity_threshold: float,
    relative_interval_tolerance: float = 1e-6,
    minimum_segment_samples: int = 2,
) -> TimeSeriesQualitySummary:
    """Segment cadence/gaps and flag large adjacent finite changes.

    Discontinuities are reported as the original index of the later sample. They
    are not classified as spike, earthquake, instrument step, or physical signal
    and no value is removed or replaced.
    """

    threshold = float(discontinuity_threshold)
    if not math.isfinite(threshold) or threshold <= 0.0:
        raise ValueError("discontinuity_threshold must be finite and positive")
    timebase = split_uniform_time_series(
        timestamps_s,
        samples,
        expected_interval_s,
        relative_interval_tolerance=relative_interval_tolerance,
        minimum_segment_samples=minimum_segment_samples,
    )
    differences = []
    flagged = []
    for segment in timebase.segments:
        for offset in range(1, len(segment.samples)):
            difference = abs(segment.samples[offset] - segment.samples[offset - 1])
            differences.append(difference)
            if difference >= threshold:
                flagged.append(segment.source_start_index + offset)
    return TimeSeriesQualitySummary(
        timebase=timebase,
        discontinuity_threshold=threshold,
        discontinuity_later_indices=tuple(flagged),
        maximum_finite_adjacent_difference=max(differences, default=0.0),
    )
