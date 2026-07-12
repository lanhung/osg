"""Shared immutable time-series contracts for process-level reference models."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ScalarGravitySignal:
    """A process source amplitude and corresponding upward-positive vertical gravity."""

    process_id: str
    times_s: tuple[float, ...]
    source_amplitude: tuple[float, ...]
    source_amplitude_unit: str
    vertical_direct_gravity_m_s2: tuple[float, ...]
    model_scope: str

    def __post_init__(self) -> None:
        if not self.process_id.strip() or not self.source_amplitude_unit.strip():
            raise ValueError("process_id and source_amplitude_unit must not be empty")
        if not self.model_scope.strip():
            raise ValueError("model_scope must not be empty")
        count = len(self.times_s)
        if count < 2:
            raise ValueError("process signal must contain at least two samples")
        if len(self.source_amplitude) != count or len(self.vertical_direct_gravity_m_s2) != count:
            raise ValueError("time, source-amplitude, and gravity arrays must have equal length")
        if not all(math.isfinite(value) for value in self.times_s):
            raise ValueError("times must be finite")
        if any(self.times_s[index + 1] <= self.times_s[index] for index in range(count - 1)):
            raise ValueError("times must be strictly increasing")
        if not all(math.isfinite(value) for value in self.source_amplitude):
            raise ValueError("source amplitudes must be finite")
        if not all(math.isfinite(value) for value in self.vertical_direct_gravity_m_s2):
            raise ValueError("gravity samples must be finite")

    @property
    def peak_absolute_gravity_m_s2(self) -> float:
        return max(abs(value) for value in self.vertical_direct_gravity_m_s2)


def regular_times(
    sample_count: int,
    sample_interval_s: float,
    *,
    start_time_s: float = 0.0,
) -> tuple[float, ...]:
    """Return an endpoint-exclusive regular time axis with exact sample count."""

    if isinstance(sample_count, bool) or not isinstance(sample_count, int) or sample_count < 2:
        raise ValueError("sample_count must be an integer of at least two")
    interval = float(sample_interval_s)
    start = float(start_time_s)
    if not math.isfinite(interval) or interval <= 0.0:
        raise ValueError("sample_interval_s must be finite and greater than zero")
    if not math.isfinite(start):
        raise ValueError("start_time_s must be finite")
    return tuple(start + index * interval for index in range(sample_count))

