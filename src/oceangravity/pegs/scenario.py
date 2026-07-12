"""Source-bound Manila megathrust scenario and tsunami-arrival contracts."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TsunamiArrival:
    """One location-specific arrival tied to a source scenario and publication."""

    location_id: str
    arrival_time_s: float
    definition: str
    source: str

    def __post_init__(self) -> None:
        if not all(value.strip() for value in (self.location_id, self.definition, self.source)):
            raise ValueError("arrival location, definition, and source must not be empty")
        if not math.isfinite(self.arrival_time_s) or self.arrival_time_s <= 0.0:
            raise ValueError("arrival_time_s must be finite and positive")


@dataclass(frozen=True, slots=True)
class ManilaScenario:
    """A fully sourced earthquake scenario; no universal tsunami arrival exists."""

    scenario_id: str
    segment: str
    moment_magnitude: float
    strike_deg: float
    dip_deg: float
    rake_deg: float
    top_depth_m: float
    rupture_length_m: float
    rupture_width_m: float
    mean_slip_m: float
    rise_time_s: float
    rupture_velocity_m_s: float
    source: str
    arrivals: tuple[TsunamiArrival, ...] = ()

    def __post_init__(self) -> None:
        if not all(value.strip() for value in (self.scenario_id, self.segment, self.source)):
            raise ValueError("scenario ID, segment, and source must not be empty")
        numeric = (
            self.moment_magnitude,
            self.strike_deg,
            self.dip_deg,
            self.rake_deg,
            self.top_depth_m,
            self.rupture_length_m,
            self.rupture_width_m,
            self.mean_slip_m,
            self.rise_time_s,
            self.rupture_velocity_m_s,
        )
        if not all(math.isfinite(value) for value in numeric):
            raise ValueError("scenario numeric parameters must be finite")
        if not 0.0 <= self.strike_deg < 360.0:
            raise ValueError("strike_deg must lie in [0, 360)")
        if not 0.0 < self.dip_deg <= 90.0:
            raise ValueError("dip_deg must lie in (0, 90]")
        if not -180.0 <= self.rake_deg <= 180.0:
            raise ValueError("rake_deg must lie in [-180, 180]")
        if self.moment_magnitude <= 0.0 or self.top_depth_m < 0.0:
            raise ValueError("magnitude must be positive and top depth non-negative")
        if not all(
            value > 0.0
            for value in (
                self.rupture_length_m,
                self.rupture_width_m,
                self.mean_slip_m,
                self.rise_time_s,
                self.rupture_velocity_m_s,
            )
        ):
            raise ValueError("rupture dimensions, slip, time, and velocity must be positive")
        locations = [arrival.location_id for arrival in self.arrivals]
        if len(set(locations)) != len(locations):
            raise ValueError("a scenario may contain only one arrival definition per location ID")
