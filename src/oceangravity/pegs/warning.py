"""Unambiguous timing and lead-time metrics for PEGS warning evaluation."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WarningTimeline:
    """Event-relative times; positive gain means PEGS characterizes earlier."""

    p_trigger_s: float
    pegs_detect_s: float
    pegs_reliable_magnitude_s: float
    conventional_reliable_magnitude_s: float
    tsunami_arrivals_s: tuple[tuple[str, float], ...]

    def __post_init__(self) -> None:
        named_times = (
            ("p_trigger_s", self.p_trigger_s),
            ("pegs_detect_s", self.pegs_detect_s),
            ("pegs_reliable_magnitude_s", self.pegs_reliable_magnitude_s),
            ("conventional_reliable_magnitude_s", self.conventional_reliable_magnitude_s),
        )
        if not all(math.isfinite(value) and value >= 0.0 for _, value in named_times):
            raise ValueError("warning times must be finite and non-negative")
        if self.pegs_reliable_magnitude_s < self.pegs_detect_s:
            raise ValueError("reliable PEGS magnitude cannot precede PEGS detection")
        locations = [location for location, _ in self.tsunami_arrivals_s]
        if not locations or len(set(locations)) != len(locations):
            raise ValueError("tsunami arrivals require unique non-empty locations")
        if any(not location.strip() for location in locations):
            raise ValueError("tsunami arrival locations must not be empty")
        if not all(
            math.isfinite(arrival) and arrival > 0.0
            for _, arrival in self.tsunami_arrivals_s
        ):
            raise ValueError("tsunami arrival times must be finite and positive")

    @property
    def characterization_gain_s(self) -> float:
        """Conventional reliable-Mw time minus PEGS reliable-Mw time."""

        return self.conventional_reliable_magnitude_s - self.pegs_reliable_magnitude_s

    @property
    def pegs_detection_relative_to_p_trigger_s(self) -> float:
        """PEGS detection minus P trigger; negative means PEGS detects first."""

        return self.pegs_detect_s - self.p_trigger_s

    def lead_times_s(self) -> dict[str, float]:
        """Location-specific arrival minus PEGS reliable decision time."""

        return {
            location: arrival - self.pegs_reliable_magnitude_s
            for location, arrival in self.tsunami_arrivals_s
        }
