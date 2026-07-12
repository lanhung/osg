"""Parametric ocean-process source and gravity-signal models."""

from .common import ScalarGravitySignal, regular_times
from .eddy import (
    CompensatedDensityEddyResult,
    translating_compensated_gaussian_density_eddy,
    translating_gaussian_surface_eddy,
)
from .gridded_load import (
    GriddedSeaLevelSignalResult,
    gridded_sea_level_direct_gravity_signal,
)
from .internal_wave import (
    CompensatedDipoleResult,
    oscillating_compensated_gaussian_dipole,
)
from .landslide import (
    MassRelocationResult,
    mass_conserving_gaussian_submarine_landslide,
    mass_conserving_submarine_landslide,
)
from .storm_surge import asymmetric_gaussian_disk_surge
from .tide import periodic_disk_tide
from .tsunami import (
    TsunamiWavePacketResult,
    gaussian_packet_amplitude_from_energy,
    propagating_compensated_gaussian_tsunami,
)

__all__ = [
    "CompensatedDensityEddyResult",
    "CompensatedDipoleResult",
    "GriddedSeaLevelSignalResult",
    "MassRelocationResult",
    "ScalarGravitySignal",
    "TsunamiWavePacketResult",
    "asymmetric_gaussian_disk_surge",
    "gaussian_packet_amplitude_from_energy",
    "gridded_sea_level_direct_gravity_signal",
    "mass_conserving_gaussian_submarine_landslide",
    "mass_conserving_submarine_landslide",
    "oscillating_compensated_gaussian_dipole",
    "periodic_disk_tide",
    "propagating_compensated_gaussian_tsunami",
    "regular_times",
    "translating_compensated_gaussian_density_eddy",
    "translating_gaussian_surface_eddy",
]
