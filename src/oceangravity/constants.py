"""Physical constants and exact unit scale factors used by the project.

All numerical kernels accept and return SI quantities unless their API explicitly
states otherwise. Keeping conversion factors here prevents implicit microgal/nm s-2
conversions from leaking into physics code.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PhysicalConstant:
    """A scalar physical constant with provenance and optional standard uncertainty."""

    value: float
    unit: str
    source: str
    standard_uncertainty: float | None = None


GRAVITATIONAL_CONSTANT = PhysicalConstant(
    value=6.67430e-11,
    unit="m^3 kg^-1 s^-2",
    source="CODATA 2018 recommended value",
    standard_uncertainty=1.5e-15,
)

STANDARD_GRAVITY = PhysicalConstant(
    value=9.80665,
    unit="m s^-2",
    source="Conventional standard gravity; exact by definition",
    standard_uncertainty=0.0,
)

REFERENCE_SEAWATER_DENSITY = PhysicalConstant(
    value=1025.0,
    unit="kg m^-3",
    source="Project reference value; scenario-specific density must override it",
)

# Exact scale factors expressed in m s^-2.
GAL = 1.0e-2
MICROGAL = 1.0e-8
NANOGAL = 1.0e-11
NANOMETRE_PER_SECOND_SQUARED = 1.0e-9


def microgal_to_si(value: float) -> float:
    """Convert microgal to metres per second squared."""

    return value * MICROGAL


def si_to_microgal(value: float) -> float:
    """Convert metres per second squared to microgal."""

    return value / MICROGAL

