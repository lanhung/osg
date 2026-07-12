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
    sample_interval_s: float
    template_duration_s: float
    decision_step_s: float
    trailing_samples_after_last_start: int
    noise_model: str
    noise_scale_source_ids: tuple[tuple[str, str], ...]


@dataclass(frozen=True, slots=True)
class CrossStationCovarianceModel:
    station_ids: tuple[str, ...]
    covariance: tuple[tuple[float, ...], ...]
    source_id: str
    calibration_window_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.station_ids or any(not value.strip() for value in self.station_ids):
            raise ValueError("covariance station IDs must be non-empty")
        if len(set(self.station_ids)) != len(self.station_ids):
            raise ValueError("covariance station IDs must be unique")
        if not self.source_id.strip():
            raise ValueError("covariance source ID must be non-empty")
        if not self.calibration_window_ids or any(
            not value.strip() for value in self.calibration_window_ids
        ):
            raise ValueError("covariance calibration window IDs must be non-empty")
        if len(set(self.calibration_window_ids)) != len(self.calibration_window_ids):
            raise ValueError("covariance calibration window IDs must be unique")
        count = len(self.station_ids)
        if len(self.covariance) != count or any(
            len(row) != count for row in self.covariance
        ):
            raise ValueError("covariance matrix dimensions must match station IDs")
        if not all(math.isfinite(value) for row in self.covariance for value in row):
            raise ValueError("covariance matrix must be finite")
        for left in range(count):
            for right in range(count):
                if not math.isclose(
                    self.covariance[left][right],
                    self.covariance[right][left],
                    rel_tol=1.0e-12,
                    abs_tol=1.0e-18,
                ):
                    raise ValueError("covariance matrix must be symmetric")
        _cholesky_factor(self.covariance)


@dataclass(frozen=True, slots=True)
class CovarianceNetworkTemplateScores:
    scores: tuple[float, ...]
    start_sample_indices: tuple[int, ...]
    discarded_start_sample_indices: tuple[int, ...]
    station_ids: tuple[str, ...]
    template_length_samples: int
    decision_step_samples: int
    sample_interval_s: float
    template_duration_s: float
    decision_step_s: float
    trailing_samples_after_last_start: int
    noise_model: str
    covariance_source_id: str
    covariance_calibration_window_ids: tuple[str, ...]


def _cholesky_factor(
    matrix: Sequence[Sequence[float]],
) -> tuple[tuple[float, ...], ...]:
    """Return lower Cholesky factor or reject a non-positive-definite matrix."""

    count = len(matrix)
    lower = [[0.0] * count for _ in range(count)]
    for row in range(count):
        for column in range(row + 1):
            subtotal = math.fsum(
                lower[row][index] * lower[column][index]
                for index in range(column)
            )
            if row == column:
                diagonal = matrix[row][row] - subtotal
                if not math.isfinite(diagonal) or diagonal <= 0.0:
                    raise ValueError("covariance matrix must be positive definite")
                lower[row][column] = math.sqrt(diagonal)
            else:
                lower[row][column] = (
                    matrix[row][column] - subtotal
                ) / lower[column][column]
    return tuple(tuple(row) for row in lower)


def _solve_cholesky(
    lower: Sequence[Sequence[float]], vector: Sequence[float]
) -> tuple[float, ...]:
    count = len(vector)
    forward = [0.0] * count
    for row in range(count):
        forward[row] = (
            vector[row]
            - math.fsum(lower[row][column] * forward[column] for column in range(row))
        ) / lower[row][row]
    solution = [0.0] * count
    for row in range(count - 1, -1, -1):
        solution[row] = (
            forward[row]
            - math.fsum(
                lower[column][row] * solution[column]
                for column in range(row + 1, count)
            )
        ) / lower[row][row]
    return tuple(solution)


def independent_noise_network_template_scores(
    station_series: Mapping[str, Sequence[float]],
    station_templates: Mapping[str, Sequence[float]],
    station_noise_standard_deviation: Mapping[str, float],
    station_noise_scale_source_ids: Mapping[str, str],
    *,
    sample_interval_s: float,
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
    if set(station_noise_scale_source_ids) != expected:
        raise ValueError("noise-scale source IDs must match station series exactly")
    if station_inclusion_masks is not None and set(station_inclusion_masks) != expected:
        raise ValueError("station mask IDs must match station series exactly")
    if (
        isinstance(decision_step_samples, bool)
        or not isinstance(decision_step_samples, int)
        or decision_step_samples <= 0
    ):
        raise ValueError("decision_step_samples must be a positive integer")
    sample_interval = float(sample_interval_s)
    if not math.isfinite(sample_interval) or sample_interval <= 0.0:
        raise ValueError("sample_interval_s must be finite and positive")

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
        sample_interval_s=sample_interval,
        template_duration_s=template_length * sample_interval,
        decision_step_s=decision_step_samples * sample_interval,
        trailing_samples_after_last_start=sample_count - (last_start + template_length),
        noise_model="independent_station_white_gaussian_reference",
        noise_scale_source_ids=tuple(
            (station_id, noise_sources[station_id]) for station_id in station_ids
        ),
    )


def cross_station_covariance_template_scores(
    station_series: Mapping[str, Sequence[float]],
    station_templates: Mapping[str, Sequence[float]],
    covariance_model: CrossStationCovarianceModel,
    *,
    sample_interval_s: float,
    decision_step_samples: int,
    station_inclusion_masks: Mapping[str, Sequence[bool]] | None = None,
) -> CovarianceNetworkTemplateScores:
    """Score a network template with cross-station covariance and white time."""

    station_ids = covariance_model.station_ids
    expected = set(station_ids)
    if set(station_series) != expected or set(station_templates) != expected:
        raise ValueError("series and template IDs must match covariance stations exactly")
    if station_inclusion_masks is not None and set(station_inclusion_masks) != expected:
        raise ValueError("station mask IDs must match covariance stations exactly")
    if isinstance(decision_step_samples, bool) or not isinstance(
        decision_step_samples, int
    ) or decision_step_samples <= 0:
        raise ValueError("decision_step_samples must be a positive integer")
    sample_interval = float(sample_interval_s)
    if not math.isfinite(sample_interval) or sample_interval <= 0.0:
        raise ValueError("sample_interval_s must be finite and positive")
    series = {
        station: tuple(float(value) for value in station_series[station])
        for station in station_ids
    }
    templates = {
        station: tuple(float(value) for value in station_templates[station])
        for station in station_ids
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
    if station_inclusion_masks is None:
        masks = {station: (True,) * sample_count for station in station_ids}
    else:
        masks = {
            station: tuple(station_inclusion_masks[station]) for station in station_ids
        }
        if any(
            len(mask) != sample_count
            or any(not isinstance(value, bool) for value in mask)
            for mask in masks.values()
        ):
            raise ValueError("every station mask must contain one boolean per sample")

    lower = _cholesky_factor(covariance_model.covariance)
    solved_templates = []
    normalization_squared = 0.0
    for offset in range(template_length):
        template_vector = tuple(templates[station][offset] for station in station_ids)
        solved = _solve_cholesky(lower, template_vector)
        solved_templates.append(solved)
        normalization_squared += math.fsum(
            template_vector[index] * solved[index]
            for index in range(len(station_ids))
        )
    if normalization_squared <= 0.0:
        raise ValueError("network templates cannot all be zero")
    normalization = math.sqrt(normalization_squared)
    starts = tuple(range(0, sample_count - template_length + 1, decision_step_samples))
    used = tuple(
        start
        for start in starts
        if all(
            all(masks[station][start : start + template_length])
            for station in station_ids
        )
    )
    used_set = set(used)
    discarded = tuple(start for start in starts if start not in used_set)
    if not used:
        raise ValueError("covariance template baseline requires one included window")
    scores = []
    for start in used:
        numerator = math.fsum(
            series[station][start + offset] * solved_templates[offset][station_index]
            for offset in range(template_length)
            for station_index, station in enumerate(station_ids)
        )
        scores.append(numerator / normalization)
    last_start = starts[-1]
    return CovarianceNetworkTemplateScores(
        scores=tuple(scores),
        start_sample_indices=used,
        discarded_start_sample_indices=discarded,
        station_ids=station_ids,
        template_length_samples=template_length,
        decision_step_samples=decision_step_samples,
        sample_interval_s=sample_interval,
        template_duration_s=template_length * sample_interval,
        decision_step_s=decision_step_samples * sample_interval,
        trailing_samples_after_last_start=sample_count - (last_start + template_length),
        noise_model="cross_station_covariance_temporally_white_reference",
        covariance_source_id=covariance_model.source_id,
        covariance_calibration_window_ids=covariance_model.calibration_window_ids,
    )
