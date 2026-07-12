"""Versioned, unit-explicit instrument amplitude spectral-density curves."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NoiseCurve:
    """One-sided amplitude spectral density (ASD) sampled at positive frequencies."""

    instrument_id: str
    observable: str
    asd_unit: str
    frequencies_hz: tuple[float, ...]
    asd: tuple[float, ...]
    source: str
    curve_version: str
    digitization_relative_uncertainty: float = 0.0

    def __post_init__(self) -> None:
        if not self.instrument_id.strip():
            raise ValueError("instrument_id must not be empty")
        if not self.observable.strip() or not self.asd_unit.strip():
            raise ValueError("observable and asd_unit must not be empty")
        if not self.source.strip() or not self.curve_version.strip():
            raise ValueError("source and curve_version must not be empty")
        if len(self.frequencies_hz) != len(self.asd) or len(self.frequencies_hz) < 2:
            raise ValueError("frequency and ASD arrays must have equal length of at least two")
        if not all(math.isfinite(value) and value > 0.0 for value in self.frequencies_hz):
            raise ValueError("noise-curve frequencies must be finite and positive")
        if any(
            self.frequencies_hz[index + 1] <= self.frequencies_hz[index]
            for index in range(len(self.frequencies_hz) - 1)
        ):
            raise ValueError("noise-curve frequencies must be strictly increasing")
        if not all(math.isfinite(value) and value > 0.0 for value in self.asd):
            raise ValueError("ASD values must be finite and positive")
        if (
            not math.isfinite(self.digitization_relative_uncertainty)
            or self.digitization_relative_uncertainty < 0.0
        ):
            raise ValueError("digitization relative uncertainty must be finite and non-negative")

    def asd_at(self, frequency_hz: float) -> float:
        """Interpolate ASD linearly in log-frequency/log-ASD space without extrapolation."""

        frequency = float(frequency_hz)
        if not math.isfinite(frequency) or frequency <= 0.0:
            raise ValueError("frequency_hz must be finite and positive")
        if frequency < self.frequencies_hz[0] or frequency > self.frequencies_hz[-1]:
            raise ValueError(
                f"frequency {frequency} Hz is outside curve range "
                f"[{self.frequencies_hz[0]}, {self.frequencies_hz[-1]}] Hz"
            )
        for index, node in enumerate(self.frequencies_hz):
            if frequency == node:
                return self.asd[index]
            if frequency < node:
                left = index - 1
                log_fraction = math.log(frequency / self.frequencies_hz[left]) / math.log(
                    node / self.frequencies_hz[left]
                )
                return math.exp(
                    math.log(self.asd[left])
                    + log_fraction * math.log(self.asd[index] / self.asd[left])
                )
        raise RuntimeError("validated frequency lookup did not find an interpolation interval")

    def psd_at(self, frequency_hz: float) -> float:
        """Return one-sided power spectral density by squaring interpolated ASD."""

        amplitude = self.asd_at(frequency_hz)
        return amplitude * amplitude

