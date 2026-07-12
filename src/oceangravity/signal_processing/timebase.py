"""Explicit cadence and gap handling before spectral analysis."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UniformTimeSeriesSegment:
    """One finite contiguous run on the declared uniform cadence."""

    source_start_index: int
    source_stop_index_exclusive: int
    timestamps_s: tuple[float, ...]
    samples: tuple[float, ...]

    def __post_init__(self) -> None:
        if len(self.timestamps_s) != len(self.samples) or len(self.samples) < 2:
            raise ValueError("a uniform segment must contain at least two timestamped samples")


@dataclass(frozen=True, slots=True)
class TimebaseSegmentationResult:
    """Segments and loss accounting; no samples are synthesized."""

    expected_interval_s: float
    relative_interval_tolerance: float
    segments: tuple[UniformTimeSeriesSegment, ...]
    missing_samples: int
    cadence_breaks: int
    dropped_short_run_samples: int
    input_samples: int

    @property
    def retained_samples(self) -> int:
        return sum(len(segment.samples) for segment in self.segments)


def split_uniform_time_series(
    timestamps_s: Sequence[float],
    samples: Sequence[float | None],
    expected_interval_s: float,
    *,
    relative_interval_tolerance: float = 1e-6,
    minimum_segment_samples: int = 2,
) -> TimebaseSegmentationResult:
    """Split at missing samples or cadence violations without interpolation.

    Timestamps must remain finite and strictly increasing even where the sample is
    missing. A cadence violation starts a new run at the later sample. Runs shorter
    than ``minimum_segment_samples`` are counted and omitted. This function never
    fills gaps, changes cadence, or applies an anti-alias filter.
    """

    if len(timestamps_s) != len(samples) or len(samples) < 2:
        raise ValueError("timestamps and samples must have equal length of at least two")
    interval = float(expected_interval_s)
    tolerance = float(relative_interval_tolerance)
    if not math.isfinite(interval) or interval <= 0.0:
        raise ValueError("expected_interval_s must be finite and positive")
    if not math.isfinite(tolerance) or tolerance < 0.0:
        raise ValueError("relative_interval_tolerance must be finite and non-negative")
    if isinstance(minimum_segment_samples, bool) or not isinstance(minimum_segment_samples, int):
        raise ValueError("minimum_segment_samples must be an integer of at least two")
    if minimum_segment_samples < 2:
        raise ValueError("minimum_segment_samples must be an integer of at least two")

    timestamps = tuple(float(value) for value in timestamps_s)
    if not all(math.isfinite(value) for value in timestamps):
        raise ValueError("timestamps must be finite")
    if any(timestamps[index + 1] <= timestamps[index] for index in range(len(timestamps) - 1)):
        raise ValueError("timestamps must be strictly increasing")
    values = tuple(
        None if value is None or not math.isfinite(float(value)) else float(value)
        for value in samples
    )

    segments: list[UniformTimeSeriesSegment] = []
    run_indices: list[int] = []
    missing_samples = 0
    cadence_breaks = 0
    dropped_short_run_samples = 0

    def close_run() -> None:
        nonlocal dropped_short_run_samples
        if len(run_indices) >= minimum_segment_samples:
            start = run_indices[0]
            stop = run_indices[-1] + 1
            segments.append(
                UniformTimeSeriesSegment(
                    source_start_index=start,
                    source_stop_index_exclusive=stop,
                    timestamps_s=tuple(timestamps[index] for index in run_indices),
                    samples=tuple(values[index] for index in run_indices),  # type: ignore[arg-type]
                )
            )
        else:
            dropped_short_run_samples += len(run_indices)
        run_indices.clear()

    absolute_tolerance = interval * tolerance
    for index, value in enumerate(values):
        if value is None:
            missing_samples += 1
            close_run()
            continue
        if run_indices:
            step = timestamps[index] - timestamps[run_indices[-1]]
            if abs(step - interval) > absolute_tolerance:
                cadence_breaks += 1
                close_run()
        run_indices.append(index)
    close_run()

    return TimebaseSegmentationResult(
        expected_interval_s=interval,
        relative_interval_tolerance=tolerance,
        segments=tuple(segments),
        missing_samples=missing_samples,
        cadence_breaks=cadence_breaks,
        dropped_short_run_samples=dropped_short_run_samples,
        input_samples=len(samples),
    )
