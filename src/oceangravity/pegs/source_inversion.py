"""Discrete PEGS source-library inversion under an explicit reference noise model."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SourceTemplateHypothesis:
    scenario_id: str
    magnitude_mw: float
    segment_id: str
    template_source_id: str
    station_templates: Mapping[str, Sequence[float]]

    def __post_init__(self) -> None:
        if (
            not self.scenario_id.strip()
            or not self.segment_id.strip()
            or not self.template_source_id.strip()
        ):
            raise ValueError("source hypothesis scenario, segment, and source IDs must be non-empty")
        if not math.isfinite(self.magnitude_mw) or self.magnitude_mw <= 0.0:
            raise ValueError("source hypothesis magnitude must be finite and positive")


@dataclass(frozen=True, slots=True)
class SourceHypothesisFit:
    scenario_id: str
    magnitude_mw: float
    segment_id: str
    template_source_id: str
    chi_square: float
    improvement_over_null_chi_square: float


@dataclass(frozen=True, slots=True)
class DiscreteSourceInversion:
    best_scenario_id: str
    estimated_magnitude_mw: float
    estimated_segment_id: str
    best_beats_null: bool
    best_is_unique: bool
    null_chi_square: float
    best_chi_square: float
    second_best_delta_chi_square: float | None
    included_sample_count: int
    station_ids: tuple[str, ...]
    source_library_id: str
    sample_interval_s: float
    window_start_time_since_origin_s: float
    window_duration_s: float
    decision_time_since_origin_s: float
    noise_scale_source_ids: tuple[tuple[str, str], ...]
    ranked_hypotheses: tuple[SourceHypothesisFit, ...]
    noise_model: str


def invert_discrete_source_library(
    station_observations: Mapping[str, Sequence[float]],
    hypotheses: Sequence[SourceTemplateHypothesis],
    station_noise_standard_deviation: Mapping[str, float],
    station_noise_scale_source_ids: Mapping[str, str],
    *,
    source_library_id: str,
    sample_interval_s: float,
    window_start_time_since_origin_s: float,
    station_inclusion_masks: Mapping[str, Sequence[bool]] | None = None,
) -> DiscreteSourceInversion:
    """Rank fixed source templates by independent white-noise chi-square.

    This is a transparent discrete baseline, not continuous source inversion.
    Magnitude and segment are copied from the winning precomputed hypothesis;
    no precision finer than the frozen library is implied.
    """

    station_ids = tuple(sorted(station_observations))
    if not station_ids or any(not station_id.strip() for station_id in station_ids):
        raise ValueError("source inversion requires non-empty station IDs")
    expected = set(station_ids)
    if set(station_noise_standard_deviation) != expected:
        raise ValueError("station noise IDs must match observations exactly")
    if set(station_noise_scale_source_ids) != expected:
        raise ValueError("noise-scale source IDs must match observations exactly")
    if station_inclusion_masks is not None and set(station_inclusion_masks) != expected:
        raise ValueError("station mask IDs must match observations exactly")
    rows = tuple(hypotheses)
    if not rows:
        raise ValueError("source inversion requires at least one hypothesis")
    if not isinstance(source_library_id, str) or not source_library_id.strip():
        raise ValueError("source_library_id must be non-empty")
    sample_interval = float(sample_interval_s)
    if not math.isfinite(sample_interval) or sample_interval <= 0.0:
        raise ValueError("sample_interval_s must be finite and positive")
    window_start = float(window_start_time_since_origin_s)
    if not math.isfinite(window_start) or window_start < 0.0:
        raise ValueError(
            "window_start_time_since_origin_s must be finite and non-negative"
        )
    scenario_ids = tuple(row.scenario_id for row in rows)
    if len(set(scenario_ids)) != len(scenario_ids):
        raise ValueError("source hypothesis scenario IDs must be unique")

    observations = {
        station_id: tuple(float(value) for value in station_observations[station_id])
        for station_id in station_ids
    }
    observation_lengths = {len(row) for row in observations.values()}
    if len(observation_lengths) != 1 or next(iter(observation_lengths)) == 0:
        raise ValueError("station observations must have equal nonzero length")
    sample_count = next(iter(observation_lengths))
    if not all(
        math.isfinite(value) for row in observations.values() for value in row
    ):
        raise ValueError("station observations must be finite")
    noise = {
        station_id: float(station_noise_standard_deviation[station_id])
        for station_id in station_ids
    }
    if not all(math.isfinite(value) and value > 0.0 for value in noise.values()):
        raise ValueError("station noise standard deviations must be finite and positive")
    noise_sources = {
        station_id: station_noise_scale_source_ids[station_id]
        for station_id in station_ids
    }
    if any(
        not isinstance(source_id, str) or not source_id.strip()
        for source_id in noise_sources.values()
    ):
        raise ValueError("noise-scale source IDs must be non-empty strings")
    if station_inclusion_masks is None:
        masks = {
            station_id: (True,) * len(observations[station_id])
            for station_id in station_ids
        }
    else:
        masks = {
            station_id: tuple(station_inclusion_masks[station_id])
            for station_id in station_ids
        }
        if any(
            len(masks[station_id]) != len(observations[station_id])
            or any(not isinstance(value, bool) for value in masks[station_id])
            for station_id in station_ids
        ):
            raise ValueError("each station mask must contain one boolean per observation")
    included_count = sum(
        include for station_id in station_ids for include in masks[station_id]
    )
    if included_count == 0:
        raise ValueError("source inversion requires at least one included sample")

    null_chi_square = math.fsum(
        observations[station_id][index] ** 2 / noise[station_id] ** 2
        for station_id in station_ids
        for index, include in enumerate(masks[station_id])
        if include
    )
    fits = []
    for hypothesis in rows:
        if set(hypothesis.station_templates) != expected:
            raise ValueError(
                f"hypothesis {hypothesis.scenario_id!r} station IDs do not match observations"
            )
        templates = {
            station_id: tuple(
                float(value) for value in hypothesis.station_templates[station_id]
            )
            for station_id in station_ids
        }
        if any(
            len(templates[station_id]) != len(observations[station_id])
            for station_id in station_ids
        ):
            raise ValueError(
                f"hypothesis {hypothesis.scenario_id!r} template length does not match observations"
            )
        if not all(math.isfinite(value) for row in templates.values() for value in row):
            raise ValueError("source hypothesis templates must be finite")
        chi_square = math.fsum(
            (
                observations[station_id][index] - templates[station_id][index]
            )
            ** 2
            / noise[station_id] ** 2
            for station_id in station_ids
            for index, include in enumerate(masks[station_id])
            if include
        )
        fits.append(
            SourceHypothesisFit(
                scenario_id=hypothesis.scenario_id,
                magnitude_mw=hypothesis.magnitude_mw,
                segment_id=hypothesis.segment_id,
                template_source_id=hypothesis.template_source_id,
                chi_square=chi_square,
                improvement_over_null_chi_square=null_chi_square - chi_square,
            )
        )
    ranked = tuple(sorted(fits, key=lambda row: (row.chi_square, row.scenario_id)))
    best = ranked[0]
    delta = None if len(ranked) == 1 else ranked[1].chi_square - best.chi_square
    return DiscreteSourceInversion(
        best_scenario_id=best.scenario_id,
        estimated_magnitude_mw=best.magnitude_mw,
        estimated_segment_id=best.segment_id,
        best_beats_null=best.improvement_over_null_chi_square > 0.0,
        best_is_unique=delta is None or delta > 0.0,
        null_chi_square=null_chi_square,
        best_chi_square=best.chi_square,
        second_best_delta_chi_square=delta,
        included_sample_count=included_count,
        station_ids=station_ids,
        source_library_id=source_library_id,
        sample_interval_s=sample_interval,
        window_start_time_since_origin_s=window_start,
        window_duration_s=sample_count * sample_interval,
        decision_time_since_origin_s=(
            window_start + sample_count * sample_interval
        ),
        noise_scale_source_ids=tuple(
            (station_id, noise_sources[station_id]) for station_id in station_ids
        ),
        ranked_hypotheses=ranked,
        noise_model="independent_station_white_gaussian_reference",
    )
