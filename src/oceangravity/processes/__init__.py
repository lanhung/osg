"""Parametric ocean-process source and gravity-signal models."""

from .common import ScalarGravitySignal, regular_times
from .eddy import (
    CompensatedDensityEddyResult,
    translating_compensated_gaussian_density_eddy,
    translating_gaussian_surface_eddy,
)
from .internal_wave import (
    CompensatedDipoleResult,
    oscillating_compensated_gaussian_dipole,
)
from .landslide import MassRelocationResult, mass_conserving_submarine_landslide
from .storm_surge import asymmetric_gaussian_disk_surge
from .tide import periodic_disk_tide
from .tsunami import TsunamiWavePacketResult, propagating_compensated_gaussian_tsunami

__all__ = [
    "ScalarGravitySignal",
    "CompensatedDipoleResult",
    "MassRelocationResult",
    "TsunamiWavePacketResult",
    "asymmetric_gaussian_disk_surge",
    "periodic_disk_tide",
    "oscillating_compensated_gaussian_dipole",
    "mass_conserving_submarine_landslide",
    "propagating_compensated_gaussian_tsunami",
    "regular_times",
    "translating_gaussian_surface_eddy",
    "translating_compensated_gaussian_density_eddy",
    "CompensatedDensityEddyResult",
]
