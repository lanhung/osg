"""Deterministic Latin-hypercube sampling and compact ensemble summaries."""

from __future__ import annotations

import math
import random
from collections.abc import Mapping, Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ParameterRange:
    name: str
    lower: float
    upper: float
    scale: str = "linear"

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("parameter name must not be empty")
        if not math.isfinite(self.lower) or not math.isfinite(self.upper):
            raise ValueError("parameter bounds must be finite")
        if self.upper <= self.lower:
            raise ValueError("parameter upper bound must exceed lower bound")
        if self.scale not in {"linear", "log"}:
            raise ValueError("parameter scale must be 'linear' or 'log'")
        if self.scale == "log" and self.lower <= 0.0:
            raise ValueError("log-scale parameter bounds must be positive")

    def transform_unit(self, unit_value: float) -> float:
        if not 0.0 <= unit_value <= 1.0:
            raise ValueError("unit_value must lie in [0, 1]")
        if self.scale == "linear":
            return self.lower + unit_value * (self.upper - self.lower)
        return math.exp(math.log(self.lower) + unit_value * math.log(self.upper / self.lower))


def latin_hypercube(
    parameters: Sequence[ParameterRange],
    sample_count: int,
    *,
    random_seed: int,
) -> tuple[dict[str, float], ...]:
    """Generate one jittered point per stratum in every parameter dimension."""

    if len(parameters) == 0:
        raise ValueError("at least one parameter range is required")
    if len({parameter.name for parameter in parameters}) != len(parameters):
        raise ValueError("parameter names must be unique")
    if isinstance(sample_count, bool) or not isinstance(sample_count, int) or sample_count <= 0:
        raise ValueError("sample_count must be a positive integer")
    if isinstance(random_seed, bool) or not isinstance(random_seed, int):
        raise ValueError("random_seed must be an integer")

    generator = random.Random(random_seed)
    dimension_values: dict[str, list[float]] = {}
    for parameter in parameters:
        unit_values = [
            (stratum + generator.random()) / sample_count for stratum in range(sample_count)
        ]
        generator.shuffle(unit_values)
        dimension_values[parameter.name] = [
            parameter.transform_unit(value) for value in unit_values
        ]
    return tuple(
        {parameter.name: dimension_values[parameter.name][sample_index] for parameter in parameters}
        for sample_index in range(sample_count)
    )


def quantile(values: Sequence[float], probability: float) -> float:
    """Return a linearly interpolated sample quantile (Hyndman-Fan type 7)."""

    if len(values) == 0:
        raise ValueError("quantile values must not be empty")
    p = float(probability)
    if not math.isfinite(p) or not 0.0 <= p <= 1.0:
        raise ValueError("quantile probability must lie in [0, 1]")
    ordered = sorted(float(value) for value in values)
    if not all(math.isfinite(value) for value in ordered):
        raise ValueError("quantile values must be finite")
    position = p * (len(ordered) - 1)
    lower_index = math.floor(position)
    upper_index = math.ceil(position)
    if lower_index == upper_index:
        return ordered[lower_index]
    fraction = position - lower_index
    return ordered[lower_index] + fraction * (ordered[upper_index] - ordered[lower_index])


def summarize_ensemble(
    metrics: Sequence[Mapping[str, float]],
    *,
    probabilities: Sequence[float] = (0.05, 0.5, 0.95),
) -> dict[str, dict[str, float]]:
    """Summarize identical metric keys into named quantiles."""

    if len(metrics) == 0:
        raise ValueError("metrics must not be empty")
    keys = tuple(metrics[0].keys())
    if any(tuple(item.keys()) != keys for item in metrics):
        raise ValueError("every metric record must have identical ordered keys")
    labels = tuple(f"q{round(float(probability) * 100):02d}" for probability in probabilities)
    if len(set(labels)) != len(labels):
        raise ValueError("quantile probabilities produce duplicate labels")
    return {
        key: {
            label: quantile([float(item[key]) for item in metrics], probability)
            for label, probability in zip(labels, probabilities, strict=True)
        }
        for key in keys
    }
