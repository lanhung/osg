"""Traceable superconducting-gravimeter feedback calibration with uncertainty."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime


def _parse_utc(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as error:
        raise ValueError("calibration validity must be an ISO UTC timestamp") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("calibration validity timestamp must include UTC")
    if parsed.utcoffset().total_seconds() != 0.0:
        raise ValueError("calibration validity timestamp must be expressed in UTC")
    return parsed


@dataclass(frozen=True, slots=True)
class GravityCalibration:
    calibration_id: str
    factor_m_s2_per_volt: float
    factor_standard_uncertainty_m_s2_per_volt: float
    voltage_offset_v: float
    gravity_offset_m_s2: float
    gravity_offset_standard_uncertainty_m_s2: float
    valid_start_utc: str
    valid_end_utc: str
    source: str

    def __post_init__(self) -> None:
        if not self.calibration_id.strip() or not self.source.strip():
            raise ValueError("calibration ID and source must be non-empty")
        finite = (
            self.factor_m_s2_per_volt,
            self.factor_standard_uncertainty_m_s2_per_volt,
            self.voltage_offset_v,
            self.gravity_offset_m_s2,
            self.gravity_offset_standard_uncertainty_m_s2,
        )
        if not all(math.isfinite(value) for value in finite):
            raise ValueError("calibration values must be finite")
        if self.factor_m_s2_per_volt == 0.0:
            raise ValueError("calibration factor cannot be zero")
        if self.factor_standard_uncertainty_m_s2_per_volt < 0.0:
            raise ValueError("factor uncertainty cannot be negative")
        if self.gravity_offset_standard_uncertainty_m_s2 < 0.0:
            raise ValueError("offset uncertainty cannot be negative")
        if _parse_utc(self.valid_start_utc) >= _parse_utc(self.valid_end_utc):
            raise ValueError("calibration validity start must precede end")


@dataclass(frozen=True, slots=True)
class CalibratedGravity:
    sample_times_utc: tuple[str, ...]
    values_m_s2: tuple[float, ...]
    standard_uncertainty_m_s2: tuple[float, ...]
    calibration_id: str


def apply_feedback_calibration(
    sample_times_utc: Sequence[str],
    feedback_voltage_v: Sequence[float],
    calibration: GravityCalibration,
) -> CalibratedGravity:
    """Convert voltage within calibration validity and propagate uncertainty."""

    raw_times = tuple(sample_times_utc)
    times = tuple(_parse_utc(value) for value in raw_times)
    voltage = tuple(float(value) for value in feedback_voltage_v)
    if not voltage or len(times) != len(voltage):
        raise ValueError("sample times and feedback voltage must have equal nonzero length")
    if not all(math.isfinite(value) for value in voltage):
        raise ValueError("feedback voltage must be finite")
    if any(times[index + 1] <= times[index] for index in range(len(times) - 1)):
        raise ValueError("calibration sample times must be strictly increasing")
    start = _parse_utc(calibration.valid_start_utc)
    end = _parse_utc(calibration.valid_end_utc)
    if any(time < start or time >= end for time in times):
        raise ValueError("refusing to apply calibration outside its validity interval")
    centered = tuple(value - calibration.voltage_offset_v for value in voltage)
    values = tuple(
        calibration.factor_m_s2_per_volt * value + calibration.gravity_offset_m_s2
        for value in centered
    )
    uncertainty = tuple(
        math.hypot(
            value * calibration.factor_standard_uncertainty_m_s2_per_volt,
            calibration.gravity_offset_standard_uncertainty_m_s2,
        )
        for value in centered
    )
    return CalibratedGravity(raw_times, values, uncertainty, calibration.calibration_id)
