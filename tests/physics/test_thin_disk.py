"""Analytic and limiting-case tests for a uniform finite thin disk."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.constants import GRAVITATIONAL_CONSTANT
from oceangravity.gravity import (
    disk_vertical_gravity_on_axis,
    vertical_gravity,
)


class TestThinDiskGravity(unittest.TestCase):
    """Validate the axial disk solution and its physical limits."""

    def test_matches_direct_analytic_expression(self) -> None:
        density = 1_250.0
        radius = 4_000.0
        separation = 1_500.0
        result = disk_vertical_gravity_on_axis(density, radius, -separation, 0.0)
        expected = (
            -2.0
            * math.pi
            * GRAVITATIONAL_CONSTANT.value
            * density
            * (1.0 - separation / math.sqrt(separation**2 + radius**2))
        )
        self.assertAlmostEqual(result, expected, delta=abs(expected) * 1.0e-15)

    def test_field_points_toward_positive_disk(self) -> None:
        below = disk_vertical_gravity_on_axis(1.0, 2.0, 0.0, -3.0)
        above = disk_vertical_gravity_on_axis(1.0, 2.0, 0.0, 3.0)
        self.assertGreater(below, 0.0)
        self.assertLess(above, 0.0)
        self.assertAlmostEqual(below, -above)

    def test_negative_anomaly_reverses_direction(self) -> None:
        positive = disk_vertical_gravity_on_axis(10.0, 20.0, -30.0, 0.0)
        negative = disk_vertical_gravity_on_axis(-10.0, 20.0, -30.0, 0.0)
        self.assertEqual(negative, -positive)

    def test_far_field_matches_equal_point_mass_below_one_percent(self) -> None:
        density = 1_025.0
        radius = 500.0
        separation = 100.0 * radius
        disk = disk_vertical_gravity_on_axis(density, radius, -separation, 0.0)
        total_mass = math.pi * radius**2 * density
        point = vertical_gravity(total_mass, (0.0, 0.0, -separation), (0.0, 0.0, 0.0))
        relative_error = abs(disk - point) / abs(point)
        self.assertLess(relative_error, 0.01)

    def test_large_disk_approaches_infinite_sheet_one_sided_limit(self) -> None:
        density = 1_025.0
        result = disk_vertical_gravity_on_axis(density, 1.0e9, -1.0, 0.0)
        limit = -2.0 * math.pi * GRAVITATIONAL_CONSTANT.value * density
        self.assertAlmostEqual(result, limit, delta=abs(limit) * 2.0e-9)

    def test_zero_density_returns_zero(self) -> None:
        self.assertEqual(disk_vertical_gravity_on_axis(0.0, 2.0, -1.0, 0.0), 0.0)

    def test_disk_plane_and_invalid_radius_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "discontinuous"):
            disk_vertical_gravity_on_axis(1.0, 2.0, 0.0, 0.0)
        for radius in (0.0, -1.0):
            with (
                self.subTest(radius=radius),
                self.assertRaisesRegex(ValueError, "greater than zero"),
            ):
                disk_vertical_gravity_on_axis(1.0, radius, -1.0, 0.0)

    def test_nonfinite_inputs_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            disk_vertical_gravity_on_axis(math.nan, 1.0, -1.0, 0.0)
        with self.assertRaises(ValueError):
            disk_vertical_gravity_on_axis(1.0, math.inf, -1.0, 0.0)


if __name__ == "__main__":
    unittest.main()
