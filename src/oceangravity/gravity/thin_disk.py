"""Analytic gravity of a uniform finite, infinitesimally thin disk."""

from __future__ import annotations

import math

from oceangravity.constants import GRAVITATIONAL_CONSTANT


def disk_vertical_gravity_on_axis(
    surface_density_kg_m2: float,
    radius_m: float,
    disk_z_m: float,
    observation_z_m: float,
) -> float:
    """Return upward-positive vertical gravity on a uniform disk's symmetry axis.

    The disk is horizontal in the local Cartesian frame. Surface density may be
    signed to represent a mass anomaly. All inputs and the output use SI units.

    The field of an ideal zero-thickness sheet is discontinuous at its plane, so
    ``disk_z_m == observation_z_m`` is rejected rather than assigned an arbitrary
    one-sided limit.
    """

    values = {
        "surface_density_kg_m2": float(surface_density_kg_m2),
        "radius_m": float(radius_m),
        "disk_z_m": float(disk_z_m),
        "observation_z_m": float(observation_z_m),
    }
    for name, value in values.items():
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")
    if values["radius_m"] <= 0.0:
        raise ValueError("radius_m must be greater than zero")

    signed_separation = values["disk_z_m"] - values["observation_z_m"]
    if signed_separation == 0.0:
        raise ValueError("thin-disk gravity is discontinuous in the disk plane")

    separation = abs(signed_separation)
    radius = values["radius_m"]
    hypotenuse = math.hypot(separation, radius)

    # Stable equivalent of 1 - h/sqrt(h^2 + R^2), avoiding cancellation at h >> R.
    geometry_factor = radius**2 / (hypotenuse * (hypotenuse + separation))
    direction = math.copysign(1.0, signed_separation)
    return (
        direction
        * 2.0
        * math.pi
        * GRAVITATIONAL_CONSTANT.value
        * values["surface_density_kg_m2"]
        * geometry_factor
    )

