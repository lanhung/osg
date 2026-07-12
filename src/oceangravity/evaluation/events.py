"""Leakage-safe event windows and Paper 2 data-gate evaluation."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class EventWindow:
    event_id: str
    event_type: str
    split_role: str
    start_utc: str
    end_utc: str
    station_ids: tuple[str, ...]
    source: str

    def __post_init__(self) -> None:
        if not self.event_id.strip() or not self.source.strip():
            raise ValueError("event ID and source must not be empty")
        if self.event_type not in {"typhoon", "storm_control", "quiet"}:
            raise ValueError("unsupported event_type")
        if self.split_role not in {"pilot_fit", "training", "held_out", "control"}:
            raise ValueError("unsupported split_role")
        if not self.station_ids or any(not station.strip() for station in self.station_ids):
            raise ValueError("station IDs must be non-empty")
        if len(set(self.station_ids)) != len(self.station_ids):
            raise ValueError("station IDs must be unique within an event")
        if self.start_datetime >= self.end_datetime:
            raise ValueError("event start must precede event end")
        if self.event_type == "typhoon" and self.split_role == "control":
            raise ValueError("a typhoon event cannot have control split role")
        if self.event_type != "typhoon" and self.split_role not in {"control", "held_out"}:
            raise ValueError("non-typhoon windows must be control or held_out")

    @property
    def start_datetime(self) -> datetime:
        return _parse_utc(self.start_utc)

    @property
    def end_datetime(self) -> datetime:
        return _parse_utc(self.end_utc)


@dataclass(frozen=True, slots=True)
class EventDesignAudit:
    event_count: int
    typhoon_count: int
    held_out_typhoon_count: int
    storm_control_count: int
    quiet_count: int
    typhoon_counts_by_station: tuple[tuple[str, int], ...]
    raw_data_gate_passes: bool
    evaluation_design_ready: bool


def audit_event_design(windows: tuple[EventWindow, ...]) -> EventDesignAudit:
    """Reject temporal leakage and evaluate raw-coverage/evaluation gates."""

    if not windows:
        raise ValueError("event design must not be empty")
    identifiers = [window.event_id for window in windows]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("event IDs must be unique")
    for left_index, left in enumerate(windows):
        for right in windows[left_index + 1 :]:
            shared_stations = set(left.station_ids) & set(right.station_ids)
            overlaps = (
                left.start_datetime < right.end_datetime
                and right.start_datetime < left.end_datetime
            )
            if shared_stations and overlaps:
                raise ValueError(
                    f"event windows {left.event_id!r} and {right.event_id!r} overlap "
                    f"at stations {sorted(shared_stations)}"
                )

    typhoons = [window for window in windows if window.event_type == "typhoon"]
    counts = Counter(station for window in typhoons for station in window.station_ids)
    one_station_three = any(count >= 3 for count in counts.values())
    two_stations_two = sum(count >= 2 for count in counts.values()) >= 2
    held_out_typhoons = sum(window.split_role == "held_out" for window in typhoons)
    storm_controls = sum(window.event_type == "storm_control" for window in windows)
    quiet = sum(window.event_type == "quiet" for window in windows)
    raw_gate = one_station_three or two_stations_two
    evaluation_ready = raw_gate and held_out_typhoons >= 1 and storm_controls >= 1 and quiet >= 3
    return EventDesignAudit(
        event_count=len(windows),
        typhoon_count=len(typhoons),
        held_out_typhoon_count=held_out_typhoons,
        storm_control_count=storm_controls,
        quiet_count=quiet,
        typhoon_counts_by_station=tuple(sorted(counts.items())),
        raw_data_gate_passes=raw_gate,
        evaluation_design_ready=evaluation_ready,
    )


def _parse_utc(value: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("UTC timestamp must be a non-empty string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"invalid ISO timestamp: {value}") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamps must include a UTC offset or Z suffix")
    if parsed.utcoffset().total_seconds() != 0.0:
        raise ValueError("timestamps must be expressed in UTC")
    return parsed
