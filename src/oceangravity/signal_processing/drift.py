"""Explicit SG drift corrections with validity and uncertainty; no fitting."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime


def _utc(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as error:
        raise ValueError("drift timestamps must be ISO UTC") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("drift timestamps must include UTC")
    if parsed.utcoffset().total_seconds() != 0.0:
        raise ValueError("drift timestamps must be expressed in UTC")
    return parsed


@dataclass(frozen=True, slots=True)
class InstrumentDriftModel:
    model_id: str
    reference_time_utc: str
    valid_start_utc: str
    valid_end_utc: str
    linear_rate_m_s2_per_s: float
    linear_rate_standard_uncertainty_m_s2_per_s: float
    quadratic_rate_m_s2_per_s2: float
    quadratic_rate_standard_uncertainty_m_s2_per_s2: float
    source: str
    rationale: str
    fit_data_role: str

    def __post_init__(self) -> None:
        if not self.model_id.strip() or not self.source.strip() or not self.rationale.strip():
            raise ValueError("drift model ID, source, and rationale must be non-empty")
        if self.fit_data_role not in {
            "external_calibration",
            "pre_event_only",
            "quiet_windows_only",
            "long_term_instrument_history",
        }:
            raise ValueError("unsupported drift fit_data_role")
        values = (
            self.linear_rate_m_s2_per_s,
            self.linear_rate_standard_uncertainty_m_s2_per_s,
            self.quadratic_rate_m_s2_per_s2,
            self.quadratic_rate_standard_uncertainty_m_s2_per_s2,
        )
        if not all(math.isfinite(value) for value in values):
            raise ValueError("drift rates and uncertainties must be finite")
        if self.linear_rate_standard_uncertainty_m_s2_per_s < 0.0:
            raise ValueError("linear drift uncertainty cannot be negative")
        if self.quadratic_rate_standard_uncertainty_m_s2_per_s2 < 0.0:
            raise ValueError("quadratic drift uncertainty cannot be negative")
        start = _utc(self.valid_start_utc)
        end = _utc(self.valid_end_utc)
        reference = _utc(self.reference_time_utc)
        if start >= end:
            raise ValueError("drift validity start must precede end")
        if not start <= reference < end:
            raise ValueError("drift reference time must lie inside validity interval")


@dataclass(frozen=True, slots=True)
class InstrumentDriftCorrection:
    corrected_m_s2: tuple[float, ...]
    removed_drift_m_s2: tuple[float, ...]
    removed_drift_standard_uncertainty_m_s2: tuple[float, ...]
    model_id: str


def apply_instrument_drift_model(
    sample_times_utc: Sequence[str],
    values_m_s2: Sequence[float],
    model: InstrumentDriftModel,
) -> InstrumentDriftCorrection:
    """Subtract a declared linear-plus-quadratic drift without extrapolation."""

    times = tuple(_utc(value) for value in sample_times_utc)
    values = tuple(float(value) for value in values_m_s2)
    if not times or len(times) != len(values):
        raise ValueError("sample times and gravity values must have equal nonzero length")
    if not all(math.isfinite(value) for value in values):
        raise ValueError("gravity values must be finite")
    if any(times[index + 1] <= times[index] for index in range(len(times) - 1)):
        raise ValueError("sample times must be strictly increasing")
    start = _utc(model.valid_start_utc)
    end = _utc(model.valid_end_utc)
    if any(time < start or time >= end for time in times):
        raise ValueError("refusing to extrapolate drift outside model validity")
    reference = _utc(model.reference_time_utc)
    elapsed = tuple((time - reference).total_seconds() for time in times)
    removed = tuple(
        math.fsum(
            (
                model.linear_rate_m_s2_per_s * seconds,
                0.5 * model.quadratic_rate_m_s2_per_s2 * seconds**2,
            )
        )
        for seconds in elapsed
    )
    uncertainty = tuple(
        math.hypot(
            seconds * model.linear_rate_standard_uncertainty_m_s2_per_s,
            0.5
            * seconds**2
            * model.quadratic_rate_standard_uncertainty_m_s2_per_s2,
        )
        for seconds in elapsed
    )
    return InstrumentDriftCorrection(
        corrected_m_s2=tuple(
            value - correction
            for value, correction in zip(values, removed, strict=True)
        ),
        removed_drift_m_s2=removed,
        removed_drift_standard_uncertainty_m_s2=uncertainty,
        model_id=model.model_id,
    )
