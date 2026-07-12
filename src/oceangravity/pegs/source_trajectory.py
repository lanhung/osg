"""Time-dependent prefix trajectory for the discrete PEGS source baseline."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from .source_inversion import (
    SourceTemplateHypothesis,
    invert_discrete_source_library,
)


@dataclass(frozen=True, slots=True)
class SourceInversionTrajectoryPoint:
    decision_sample_count: int
    decision_time_since_origin_s: float
    best_scenario_id: str
    estimated_magnitude_mw: float
    estimated_segment_id: str
    best_beats_null: bool
    best_is_unique: bool
    improvement_over_null_chi_square: float
    second_best_delta_chi_square: float | None
    included_sample_count: int


@dataclass(frozen=True, slots=True)
class SourceInversionTrajectory:
    source_library_id: str
    sample_interval_s: float
    window_start_time_since_origin_s: float
    station_ids: tuple[str, ...]
    noise_scale_source_ids: tuple[tuple[str, str], ...]
    points: tuple[SourceInversionTrajectoryPoint, ...]
    interpretation: str


def invert_discrete_source_library_over_time(
    station_observations: Mapping[str, Sequence[float]],
    hypotheses: Sequence[SourceTemplateHypothesis],
    station_noise_standard_deviation: Mapping[str, float],
    station_noise_scale_source_ids: Mapping[str, str],
    *,
    source_library_id: str,
    sample_interval_s: float,
    window_start_time_since_origin_s: float,
    decision_sample_counts: Sequence[int],
    station_inclusion_masks: Mapping[str, Sequence[bool]] | None = None,
) -> SourceInversionTrajectory:
    """Evaluate the same frozen source library on increasing data prefixes."""

    counts = tuple(decision_sample_counts)
    if not counts or any(
        isinstance(value, bool) or not isinstance(value, int) or value <= 0
        for value in counts
    ):
        raise ValueError("decision sample counts must be positive integers")
    if any(counts[index + 1] <= counts[index] for index in range(len(counts) - 1)):
        raise ValueError("decision sample counts must be strictly increasing")
    observation_rows = {
        station_id: tuple(values) for station_id, values in station_observations.items()
    }
    if not observation_rows:
        raise ValueError("source trajectory requires station observations")
    lengths = {len(values) for values in observation_rows.values()}
    if len(lengths) != 1 or next(iter(lengths)) == 0:
        raise ValueError("trajectory station observations must have equal nonzero length")
    sample_count = next(iter(lengths))
    if counts[-1] > sample_count:
        raise ValueError("decision sample count exceeds observation length")
    rows = tuple(hypotheses)
    if not rows:
        raise ValueError("source trajectory requires hypotheses")
    masks = None
    if station_inclusion_masks is not None:
        masks = {
            station_id: tuple(values)
            for station_id, values in station_inclusion_masks.items()
        }

    points = []
    first_inversion = None
    for count in counts:
        prefix_hypotheses = tuple(
            SourceTemplateHypothesis(
                scenario_id=row.scenario_id,
                magnitude_mw=row.magnitude_mw,
                segment_id=row.segment_id,
                template_source_id=row.template_source_id,
                station_templates={
                    station_id: tuple(values[:count])
                    for station_id, values in row.station_templates.items()
                },
            )
            for row in rows
        )
        inversion = invert_discrete_source_library(
            {
                station_id: values[:count]
                for station_id, values in observation_rows.items()
            },
            prefix_hypotheses,
            station_noise_standard_deviation,
            station_noise_scale_source_ids,
            source_library_id=source_library_id,
            sample_interval_s=sample_interval_s,
            window_start_time_since_origin_s=window_start_time_since_origin_s,
            station_inclusion_masks=(
                None
                if masks is None
                else {station_id: values[:count] for station_id, values in masks.items()}
            ),
        )
        if first_inversion is None:
            first_inversion = inversion
        best = inversion.ranked_hypotheses[0]
        points.append(
            SourceInversionTrajectoryPoint(
                decision_sample_count=count,
                decision_time_since_origin_s=inversion.decision_time_since_origin_s,
                best_scenario_id=inversion.best_scenario_id,
                estimated_magnitude_mw=inversion.estimated_magnitude_mw,
                estimated_segment_id=inversion.estimated_segment_id,
                best_beats_null=inversion.best_beats_null,
                best_is_unique=inversion.best_is_unique,
                improvement_over_null_chi_square=(
                    best.improvement_over_null_chi_square
                ),
                second_best_delta_chi_square=(
                    inversion.second_best_delta_chi_square
                ),
                included_sample_count=inversion.included_sample_count,
            )
        )
    assert first_inversion is not None
    return SourceInversionTrajectory(
        source_library_id=source_library_id,
        sample_interval_s=first_inversion.sample_interval_s,
        window_start_time_since_origin_s=(
            first_inversion.window_start_time_since_origin_s
        ),
        station_ids=first_inversion.station_ids,
        noise_scale_source_ids=first_inversion.noise_scale_source_ids,
        points=tuple(points),
        interpretation=(
            "prefix_library_ranking_not_reliable_magnitude_without_heldout_gates"
        ),
    )
