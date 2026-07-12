"""Analytic, finite-difference, and far-field tests for axial disk Tzz."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.constants import GRAVITATIONAL_CONSTANT
from oceangravity.gravity import (
    disk_vertical_gravity_gradient_on_axis,
    disk_vertical_gravity_on_axis,
    gravity_gradient_tensor,
)


class TestDiskVerticalGradient(unittest.TestCase):
    def test_matches_central_difference_of_independent_gravity(self) -> None:
        density = 1_025.0
        radius = 4_000.0
        disk_z = -2_000.0
        observation_z = 1_000.0
        step = 0.01
        numerical = (
            disk_vertical_gravity_on_axis(density, radius, disk_z, observation_z + step)
            - disk_vertical_gravity_on_axis(density, radius, disk_z, observation_z - step)
        ) / (2.0 * step)
        analytic = disk_vertical_gravity_gradient_on_axis(density, radius, disk_z, observation_z)
        self.assertAlmostEqual(numerical, analytic, delta=abs(analytic) * 1e-8)

    def test_far_field_matches_equal_point_mass_tzz(self) -> None:
        density = 1_025.0
        radius = 100.0
        separation = 100.0 * radius
        disk = disk_vertical_gravity_gradient_on_axis(density, radius, -separation, 0.0)
        mass = math.pi * radius**2 * density
        point = gravity_gradient_tensor(mass, (0.0, 0.0, -separation), (0.0, 0.0, 0.0))[2][2]
        self.assertLess(abs(disk - point) / abs(point), 0.01)

    def test_gradient_is_even_across_plane_and_signed_with_density(self) -> None:
        above = disk_vertical_gravity_gradient_on_axis(3.0, 4.0, 0.0, 5.0)
        below = disk_vertical_gravity_gradient_on_axis(3.0, 4.0, 0.0, -5.0)
        negative = disk_vertical_gravity_gradient_on_axis(-3.0, 4.0, 0.0, 5.0)
        self.assertEqual(above, below)
        self.assertEqual(negative, -above)

    def test_large_disk_gradient_tends_to_zero(self) -> None:
        first = disk_vertical_gravity_gradient_on_axis(1.0, 1.0e6, 0.0, 1.0)
        second = disk_vertical_gravity_gradient_on_axis(1.0, 1.0e9, 0.0, 1.0)
        self.assertLess(second, first / 100.0)
        self.assertGreater(first, 0.0)
        self.assertGreater(GRAVITATIONAL_CONSTANT.value, 0.0)

    def test_plane_and_invalid_radius_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            disk_vertical_gravity_gradient_on_axis(1.0, 1.0, 0.0, 0.0)
        with self.assertRaises(ValueError):
            disk_vertical_gravity_gradient_on_axis(1.0, 0.0, 0.0, 1.0)


if __name__ == "__main__":
    unittest.main()
