"""Paper 3 station-epoch readiness and operational-access auditing."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StationEpochReadiness:
    """Frozen availability facts for one broadband station epoch."""

    epoch_id: str
    network: str
    station: str
    location: str
    channels: tuple[str, ...]
    response_status: str
    waveform_status: str
    license_status: str
    latency_class: str
    noise_qc_complete: bool

    def __post_init__(self) -> None:
        if not self.epoch_id.strip() or not self.network.strip() or not self.station.strip():
            raise ValueError("epoch, network, and station IDs must be non-empty")
        if not self.channels or len(set(self.channels)) != len(self.channels):
            raise ValueError("channels must be non-empty and unique")
        if any(len(channel) != 3 or channel[:2] not in {"BH", "LH"} for channel in self.channels):
            raise ValueError("channels must be BH? or LH? broadband codes")
        if len({channel[:2] for channel in self.channels}) != 1:
            raise ValueError("one readiness epoch cannot mix BH and LH bands")
        if self.response_status not in {"verified_full", "partial", "missing", "unchecked"}:
            raise ValueError("unsupported response_status")
        if self.waveform_status not in {"downloadable", "restricted", "unavailable", "unchecked"}:
            raise ValueError("unsupported waveform_status")
        if self.license_status not in {"permitted", "restricted", "unknown"}:
            raise ValueError("unsupported license_status")
        if self.latency_class not in {
            "real_time",
            "near_real_time",
            "archive_only",
            "unknown",
        }:
            raise ValueError("unsupported latency_class")

    @property
    def has_three_component_triplet(self) -> bool:
        components = {channel[2] for channel in self.channels}
        return "Z" in components and (
            {"N", "E"}.issubset(components) or {"1", "2"}.issubset(components)
        )

    @property
    def station_id(self) -> str:
        return f"{self.network}.{self.station}"


@dataclass(frozen=True, slots=True)
class StationReadinessAudit:
    epoch_count: int
    retrospective_ready_epoch_ids: tuple[str, ...]
    operational_ready_epoch_ids: tuple[str, ...]
    ineligible_epochs: tuple[tuple[str, tuple[str, ...]], ...]
    retrospective_station_count: int
    operational_station_count: int
    inventory_smoke_gate_passes: bool


def audit_station_readiness(
    epochs: tuple[StationEpochReadiness, ...],
    *,
    minimum_operational_station_count: int,
) -> StationReadinessAudit:
    """Separate archive-analysis readiness from plausible operational access."""

    if (
        isinstance(minimum_operational_station_count, bool)
        or minimum_operational_station_count <= 0
    ):
        raise ValueError("minimum_operational_station_count must be a positive integer")
    identifiers = [epoch.epoch_id for epoch in epochs]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("epoch_id values must be unique")
    retrospective = []
    operational = []
    ineligible = []
    for epoch in epochs:
        reasons = []
        if not epoch.has_three_component_triplet:
            reasons.append("missing_three_component_triplet")
        if epoch.response_status != "verified_full":
            reasons.append("full_response_not_verified")
        if epoch.waveform_status != "downloadable":
            reasons.append("waveform_not_downloadable")
        if epoch.license_status != "permitted":
            reasons.append("license_not_permitted")
        if not epoch.noise_qc_complete:
            reasons.append("noise_qc_incomplete")
        if reasons:
            ineligible.append((epoch.epoch_id, tuple(reasons)))
            continue
        retrospective.append(epoch)
        if epoch.latency_class in {"real_time", "near_real_time"}:
            operational.append(epoch)

    retrospective_stations = {epoch.station_id for epoch in retrospective}
    operational_stations = {epoch.station_id for epoch in operational}
    return StationReadinessAudit(
        epoch_count=len(epochs),
        retrospective_ready_epoch_ids=tuple(sorted(epoch.epoch_id for epoch in retrospective)),
        operational_ready_epoch_ids=tuple(sorted(epoch.epoch_id for epoch in operational)),
        ineligible_epochs=tuple(sorted(ineligible)),
        retrospective_station_count=len(retrospective_stations),
        operational_station_count=len(operational_stations),
        inventory_smoke_gate_passes=(
            len(operational_stations) >= minimum_operational_station_count
        ),
    )
