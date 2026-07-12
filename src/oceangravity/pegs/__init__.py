"""Prompt elasto-gravity signal simulation and detection."""

from .scenario import ManilaScenario, TsunamiArrival
from .warning import WarningTimeline

__all__ = ["ManilaScenario", "TsunamiArrival", "WarningTimeline"]
