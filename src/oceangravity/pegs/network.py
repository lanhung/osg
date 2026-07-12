"""Interpretable coherent network baseline and deterministic outage masks."""

from __future__ import annotations

import math
import random
from collections.abc import Mapping, Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class NetworkPerformance:
    """Frozen operational metrics for one station-network candidate.

    Lower values are better for times, false alarms, errors, and cost; higher
    values are better for detection probability. A candidate remains explicit
    rather than being collapsed into a scientifically arbitrary weighted score.
    """

    network_id: str
    station_ids: tuple[str, ...]
    detection_time_s: float
    detection_probability: float
    false_alarms_per_30_days: float
    magnitude_mae: float
    station_cost: float

    def __post_init__(self) -> None:
        if not self.network_id.strip():
            raise ValueError("network_id must be non-empty")
        if not self.station_ids or any(not station.strip() for station in self.station_ids):
            raise ValueError("station_ids must contain non-empty station names")
        if len(set(self.station_ids)) != len(self.station_ids):
            raise ValueError("station_ids must be unique")
        finite_nonnegative = (
            self.detection_time_s,
            self.false_alarms_per_30_days,
            self.magnitude_mae,
            self.station_cost,
        )
        if not all(math.isfinite(value) and value >= 0.0 for value in finite_nonnegative):
            raise ValueError("time, false alarms, error, and cost must be finite and nonnegative")
        if (
            not math.isfinite(self.detection_probability)
            or not 0.0 <= self.detection_probability <= 1.0
        ):
            raise ValueError("detection_probability must lie in [0, 1]")


def _dominates(left: NetworkPerformance, right: NetworkPerformance) -> bool:
    """Return whether ``left`` is no worse everywhere and better somewhere."""

    no_worse = (
        left.detection_time_s <= right.detection_time_s
        and left.detection_probability >= right.detection_probability
        and left.false_alarms_per_30_days <= right.false_alarms_per_30_days
        and left.magnitude_mae <= right.magnitude_mae
        and left.station_cost <= right.station_cost
    )
    strictly_better = (
        left.detection_time_s < right.detection_time_s
        or left.detection_probability > right.detection_probability
        or left.false_alarms_per_30_days < right.false_alarms_per_30_days
        or left.magnitude_mae < right.magnitude_mae
        or left.station_cost < right.station_cost
    )
    return no_worse and strictly_better


def pareto_optimal_networks(
    candidates: Sequence[NetworkPerformance],
) -> tuple[NetworkPerformance, ...]:
    """Return the deterministic non-dominated multi-objective network frontier.

    Exact duplicate network identifiers are rejected. The result is sorted by
    identifier so input order cannot change serialized experiment outputs.
    """

    rows = tuple(candidates)
    if not rows:
        raise ValueError("at least one network candidate is required")
    identifiers = [row.network_id for row in rows]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("network_id values must be unique")
    frontier = [
        candidate
        for candidate in rows
        if not any(
            _dominates(other, candidate)
            for other in rows
            if other.network_id != candidate.network_id
        )
    ]
    return tuple(sorted(frontier, key=lambda row: row.network_id))


def coherent_network_stack(
    aligned_station_series: Mapping[str, Sequence[float]],
    *,
    station_weights: Mapping[str, float] | None = None,
) -> tuple[float, ...]:
    """L2-normalized weighted sum of already aligned station series."""

    if not aligned_station_series:
        raise ValueError("at least one aligned station series is required")
    station_ids = tuple(sorted(aligned_station_series))
    rows = {
        station: tuple(float(value) for value in aligned_station_series[station])
        for station in station_ids
    }
    lengths = {len(row) for row in rows.values()}
    if len(lengths) != 1 or next(iter(lengths)) == 0:
        raise ValueError("station series must have equal nonzero length")
    if not all(math.isfinite(value) for row in rows.values() for value in row):
        raise ValueError("station series must be finite")

    if station_weights is None:
        weights = {station: 1.0 for station in station_ids}
    else:
        if set(station_weights) != set(station_ids):
            raise ValueError("station weights must match station IDs exactly")
        weights = {station: float(station_weights[station]) for station in station_ids}
        if not all(math.isfinite(value) for value in weights.values()):
            raise ValueError("station weights must be finite")
    norm = math.sqrt(math.fsum(value * value for value in weights.values()))
    if norm == 0.0:
        raise ValueError("station weights cannot all be zero")
    normalized = {station: weights[station] / norm for station in station_ids}
    sample_count = next(iter(lengths))
    return tuple(
        math.fsum(normalized[station] * rows[station][index] for station in station_ids)
        for index in range(sample_count)
    )


def generate_station_outage_masks(
    station_ids: Sequence[str],
    outage_fraction: float,
    trial_count: int,
    *,
    random_seed: int,
) -> tuple[tuple[str, ...], ...]:
    """Return sorted available-station IDs after fixed-count random outages."""

    stations = tuple(station_ids)
    if not stations or any(not station.strip() for station in stations):
        raise ValueError("station IDs must be non-empty strings")
    if len(set(stations)) != len(stations):
        raise ValueError("station IDs must be unique")
    fraction = float(outage_fraction)
    if not math.isfinite(fraction) or not 0.0 <= fraction < 1.0:
        raise ValueError("outage_fraction must lie in [0, 1)")
    if isinstance(trial_count, bool) or not isinstance(trial_count, int) or trial_count <= 0:
        raise ValueError("trial_count must be a positive integer")
    if isinstance(random_seed, bool) or not isinstance(random_seed, int):
        raise ValueError("random_seed must be an integer")
    outage_count = round(fraction * len(stations))
    if outage_count >= len(stations):
        raise ValueError("outage setting must leave at least one station")
    generator = random.Random(random_seed)
    masks = []
    for _ in range(trial_count):
        unavailable = set(generator.sample(stations, outage_count))
        masks.append(tuple(sorted(station for station in stations if station not in unavailable)))
    return tuple(masks)
