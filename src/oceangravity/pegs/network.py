"""Interpretable coherent network baseline and deterministic outage masks."""

from __future__ import annotations

import math
import random
from collections.abc import Mapping, Sequence


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
