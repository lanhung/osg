"""Interpretable multi-station PEGS template statistic under independent noise."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NetworkTemplateScores:
    scores: tuple[float, ...]
    start_sample_indices: tuple[int, ...]
    discarded_start_sample_indices: tuple[int, ...]
    station_ids: tuple[str, ...]
    template_length_samples: int
    decision_step_samples: int
    trailing_samples_after_last_start: int
    noise_model: str


def independent_noise_network_template_scores(
    station_series: Mapping[str, Sequence[float]],
    station_templates: Mapping[str, Sequence[float]],
    station_noise_standard_deviation: Mapping[str, float],
    *,
    decision_step_samples: int,
    station_inclusion_masks: Mapping[str, Sequence[bool]] | None = None,
) -> NetworkTemplateScores:
    """Slide one aligned network template and return normalized signed scores.

    For station ``k`` and sample ``i``, the score is

    ``sum(d_ki t_ki / sigma_k^2) / sqrt(sum(t_ki^2 / sigma_k^2))``.

    It is a unit-variance signed statistic only for zero-mean, temporally white,
    independent Gaussian station noise with correctly estimated ``sigma_k``.
    Real-noise false-alarm calibration remains mandatory. Template polarity is
    retained, so a physically predicted negative response must be encoded with a
    negative template rather than converted to absolute amplitude.
    """

    station_ids = tuple(sorted(station_series))
    if not station_ids or any(not station_id.strip() for station_id in station_ids):
        raise ValueError("station series require non-empty station IDs")
    expected = set(station_ids)
    if set(station_templates) != expected:
        raise ValueError("station template IDs must match station series exactly")
    if set(station_noise_standard_deviation) != expected:
        raise ValueError("station noise IDs must match station series exactly")
    if station_inclusion_masks is not None and set(station_inclusion_masks) != expected:
        raise ValueError("station mask IDs must match station series exactly")
    if (
        isinstance(decision_step_samples, bool)
        or not isinstance(decision_step_samples, int)
        or decision_step_samples <= 0
    ):
        raise ValueError("decision_step_samples must be a positive integer")

    series = {
        station_id: tuple(float(value) for value in station_series[station_id])
        for station_id in station_ids
    }
    templates = {
        station_id: tuple(float(value) for value in station_templates[station_id])
        for station_id in station_ids
    }
    series_lengths = {len(row) for row in series.values()}
    template_lengths = {len(row) for row in templates.values()}
    if len(series_lengths) != 1 or next(iter(series_lengths)) == 0:
        raise ValueError("station series must have equal nonzero length")
    if len(template_lengths) != 1 or next(iter(template_lengths)) == 0:
        raise ValueError("station templates must have equal nonzero length")
    sample_count = next(iter(series_lengths))
    template_length = next(iter(template_lengths))
    if sample_count < template_length:
        raise ValueError("station series are shorter than the network template")
    if not all(
        math.isfinite(value)
        for rows in (series.values(), templates.values())
        for row in rows
        for value in row
    ):
        raise ValueError("station series and templates must be finite")
    noise = {
        station_id: float(station_noise_standard_deviation[station_id])
        for station_id in station_ids
    }
    if not all(math.isfinite(value) and value > 0.0 for value in noise.values()):
        raise ValueError("station noise standard deviations must be finite and positive")
    if station_inclusion_masks is None:
        masks = {station_id: (True,) * sample_count for station_id in station_ids}
    else:
        masks = {station_id: tuple(station_inclusion_masks[station_id]) for station_id in station_ids}
        if any(
            len(mask) != sample_count or any(not isinstance(value, bool) for value in mask)
            for mask in masks.values()
        ):
            raise ValueError("every station mask must contain one boolean per sample")

    normalization_squared = math.fsum(
        value * value / noise[station_id] ** 2
        for station_id in station_ids
        for value in templates[station_id]
    )
    if normalization_squared == 0.0:
        raise ValueError("network templates cannot all be zero")
    normalization = math.sqrt(normalization_squared)
    starts = tuple(range(0, sample_count - template_length + 1, decision_step_samples))
    used = tuple(
        start
        for start in starts
        if all(
            all(masks[station_id][start : start + template_length])
            for station_id in station_ids
        )
    )
    used_set = set(used)
    discarded = tuple(start for start in starts if start not in used_set)
    if not used:
        raise ValueError("network template baseline requires one fully included window")

    scores = []
    for start in used:
        numerator = math.fsum(
            series[station_id][start + offset]
            * templates[station_id][offset]
            / noise[station_id] ** 2
            for station_id in station_ids
            for offset in range(template_length)
        )
        scores.append(numerator / normalization)
    last_start = starts[-1]
    return NetworkTemplateScores(
        scores=tuple(scores),
        start_sample_indices=used,
        discarded_start_sample_indices=discarded,
        station_ids=station_ids,
        template_length_samples=template_length,
        decision_step_samples=decision_step_samples,
        trailing_samples_after_last_start=sample_count - (last_start + template_length),
        noise_model="independent_station_white_gaussian_reference",
    )
