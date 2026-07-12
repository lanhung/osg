"""Versioned, unit-explicit instrument amplitude spectral-density curves."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path


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
    interpretation: str = ""
    operating_conditions: str = ""
    model_uncertainty_note: str = ""

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
                if self.asd[left] == self.asd[index]:
                    return self.asd[left]
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


def load_noise_curves(path: str | Path) -> dict[str, NoiseCurve]:
    """Load versioned noise curves from the project JSON interchange format."""

    source_path = Path(path)
    document = json.loads(source_path.read_text(encoding="utf-8"))
    if document.get("schema_version") != 1:
        raise ValueError("unsupported instrument noise-curve schema version")
    raw_curves = document.get("curves")
    if not isinstance(raw_curves, list) or len(raw_curves) == 0:
        raise ValueError("instrument curve document must contain a non-empty curves list")
    curves: dict[str, NoiseCurve] = {}
    for raw in raw_curves:
        curve = NoiseCurve(
            instrument_id=raw["instrument_id"],
            observable=raw["observable"],
            asd_unit=raw["asd_unit"],
            frequencies_hz=tuple(raw["frequencies_hz"]),
            asd=tuple(raw["asd"]),
            source=raw["source"],
            curve_version=raw["curve_version"],
            digitization_relative_uncertainty=raw.get("digitization_relative_uncertainty", 0.0),
            interpretation=raw.get("interpretation", ""),
            operating_conditions=raw.get("operating_conditions", ""),
            model_uncertainty_note=raw.get("model_uncertainty_note", ""),
        )
        if curve.instrument_id in curves:
            raise ValueError(f"duplicate instrument_id: {curve.instrument_id}")
        curves[curve.instrument_id] = curve
    return curves
