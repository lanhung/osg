"""Non-destructive quality annotations and frozen exclusion actions."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime

ALLOWED_FLAGS = {
    "candidate_spike",
    "confirmed_instrument_spike",
    "earthquake",
    "maintenance",
    "timing_issue",
    "sensor_saturation",
    "gap_edge_buffer",
}
ALLOWED_ACTIONS = {
    "retain",
    "exclude_from_fit",
    "exclude_from_fit_and_metrics",
}


def _utc(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as error:
        raise ValueError("quality annotation timestamps must be ISO UTC") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("quality annotation timestamps must include UTC")
    if parsed.utcoffset().total_seconds() != 0.0:
        raise ValueError("quality annotation timestamps must be expressed in UTC")
    return parsed


@dataclass(frozen=True, slots=True)
class DataQualityAnnotation:
    annotation_id: str
    flag_type: str
    start_utc: str
    end_utc: str
    source: str
    rationale: str

    def __post_init__(self) -> None:
        if not self.annotation_id.strip() or not self.source.strip() or not self.rationale.strip():
            raise ValueError("annotation ID, source, and rationale must be non-empty")
        if self.flag_type not in ALLOWED_FLAGS:
            raise ValueError("unsupported quality flag type")
        if _utc(self.start_utc) >= _utc(self.end_utc):
            raise ValueError("quality annotation start must precede end")


@dataclass(frozen=True, slots=True)
class QualityAnnotationResult:
    sample_times_utc: tuple[str, ...]
    original_values: tuple[float, ...]
    annotation_ids_by_sample: tuple[tuple[str, ...], ...]
    fit_included: tuple[bool, ...]
    metric_included: tuple[bool, ...]
    policy_id: str


def apply_quality_annotations(
    sample_times_utc: Sequence[str],
    values: Sequence[float],
    annotations: Sequence[DataQualityAnnotation],
    action_by_flag: Mapping[str, str],
    *,
    policy_id: str,
) -> QualityAnnotationResult:
    """Return masks and annotations without deleting or changing any sample."""

    if not policy_id.strip():
        raise ValueError("policy_id must be non-empty")
    raw_times = tuple(sample_times_utc)
    times = tuple(_utc(value) for value in raw_times)
    samples = tuple(float(value) for value in values)
    if not samples or len(times) != len(samples):
        raise ValueError("sample times and values must have equal nonzero length")
    if not all(math.isfinite(value) for value in samples):
        raise ValueError("quality-annotated values must be finite")
    if any(times[index + 1] <= times[index] for index in range(len(times) - 1)):
        raise ValueError("quality sample times must be strictly increasing")
    if set(action_by_flag) != ALLOWED_FLAGS:
        missing = sorted(ALLOWED_FLAGS - set(action_by_flag))
        extra = sorted(set(action_by_flag) - ALLOWED_FLAGS)
        raise ValueError(f"quality policy flags must match exactly; missing={missing}, extra={extra}")
    if any(action not in ALLOWED_ACTIONS for action in action_by_flag.values()):
        raise ValueError("quality policy contains an unsupported action")
    rows = tuple(annotations)
    if len({row.annotation_id for row in rows}) != len(rows):
        raise ValueError("quality annotation IDs must be unique")

    annotations_by_sample: list[list[DataQualityAnnotation]] = [
        [] for _ in samples
    ]
    for row in rows:
        start = _utc(row.start_utc)
        end = _utc(row.end_utc)
        matched = False
        for index, time in enumerate(times):
            if start <= time < end:
                annotations_by_sample[index].append(row)
                matched = True
        if not matched:
            raise ValueError(
                f"quality annotation {row.annotation_id!r} matches no samples"
            )

    fit = []
    metric = []
    identifiers = []
    for sample_rows in annotations_by_sample:
        actions = {action_by_flag[row.flag_type] for row in sample_rows}
        identifiers.append(tuple(sorted(row.annotation_id for row in sample_rows)))
        excludes_metrics = "exclude_from_fit_and_metrics" in actions
        excludes_fit = excludes_metrics or "exclude_from_fit" in actions
        fit.append(not excludes_fit)
        metric.append(not excludes_metrics)
    return QualityAnnotationResult(
        sample_times_utc=raw_times,
        original_values=samples,
        annotation_ids_by_sample=tuple(identifiers),
        fit_included=tuple(fit),
        metric_included=tuple(metric),
        policy_id=policy_id,
    )
