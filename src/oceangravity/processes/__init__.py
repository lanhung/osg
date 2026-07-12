"""Parametric ocean-process source and gravity-signal models."""

from .common import ScalarGravitySignal, regular_times
from .tide import periodic_disk_tide

__all__ = ["ScalarGravitySignal", "periodic_disk_tide", "regular_times"]

