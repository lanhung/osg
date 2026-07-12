"""Physics and convergence tests for numerical disk integration."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.gravity import (
    disk_gravity_numerical,
    disk_vertical_gravity_on_axis,
    gravity_vector,
)


class TestNumericalDiskGravity(unittest.TestCase):
    def test_on_axis_agrees_with_analytic_solution(self) -> None:
        density = 1_025.0
        radius = 1_000.0
        center = (0.0, 0.0, -400.0)
        observation = (0.0, 0.0, 0.0)
        result = disk_gravity_numerical(
            density, radius, center, observation, radial_cells=128, angular_cells=32
        )
        analytic = disk_vertical_gravity_on_axis(density, radius, center[2], observation[2])
        relative_error = abs(result[2] - analytic) / abs(analytic)
        self.assertLess(relative_error, 1.0e-4)
        self.assertAlmostEqual(result[0], 0.0, delta=abs(analytic) * 1.0e-14)
        self.assertAlmostEqual(result[1], 0.0, delta=abs(analytic) * 1.0e-14)

    def test_off_axis_reflection_symmetry(self) -> None:
        kwargs = {"radial_cells": 64, "angular_cells": 192}
        right = disk_gravity_numerical(10.0, 20.0, (0.0, 0.0, -5.0), (8.0, 0.0, 0.0), **kwargs)
        left = disk_gravity_numerical(10.0, 20.0, (0.0, 0.0, -5.0), (-8.0, 0.0, 0.0), **kwargs)
        self.assertAlmostEqual(right[0], -left[0], delta=abs(right[0]) * 1.0e-13)
        self.assertAlmostEqual(right[1], 0.0, delta=abs(right[0]) * 1.0e-13)
        self.assertAlmostEqual(left[1], 0.0, delta=abs(left[0]) * 1.0e-13)
        self.assertAlmostEqual(right[2], left[2], delta=abs(right[2]) * 1.0e-13)

    def test_translation_invariance(self) -> None:
        kwargs = {"radial_cells": 32, "angular_cells": 48}
        base = disk_gravity_numerical(3.0, 4.0, (1.0, 2.0, -3.0), (5.0, 7.0, 8.0), **kwargs)
        shifted = disk_gravity_numerical(
            3.0, 4.0, (101.0, -198.0, 47.0), (105.0, -193.0, 58.0), **kwargs
        )
        for first, second in zip(base, shifted, strict=True):
            self.assertAlmostEqual(first, second, delta=max(abs(first), 1.0e-30) * 1.0e-14)

    def test_negative_anomaly_reverses_vector(self) -> None:
        kwargs = {"radial_cells": 24, "angular_cells": 36}
        positive = disk_gravity_numerical(7.0, 5.0, (0.0, 0.0, -2.0), (3.0, 1.0, 4.0), **kwargs)
        negative = disk_gravity_numerical(-7.0, 5.0, (0.0, 0.0, -2.0), (3.0, 1.0, 4.0), **kwargs)
        self.assertEqual(negative, tuple(-component for component in positive))

    def test_far_field_matches_area_preserving_point_mass(self) -> None:
        density = 1_025.0
        radius = 100.0
        separation = 100.0 * radius
        disk = disk_gravity_numerical(
            density,
            radius,
            (0.0, 0.0, -separation),
            (0.0, 0.0, 0.0),
            radial_cells=16,
            angular_cells=24,
        )
        mass = math.pi * radius**2 * density
        point = gravity_vector(mass, (0.0, 0.0, -separation), (0.0, 0.0, 0.0))
        relative_error = abs(disk[2] - point[2]) / abs(point[2])
        self.assertLess(relative_error, 0.01)

    def test_radial_refinement_reduces_analytic_error(self) -> None:
        density = 1.0
        radius = 2.0
        center_z = -0.7
        expected = disk_vertical_gravity_on_axis(density, radius, center_z, 0.0)
        errors = []
        for radial_cells in (8, 16, 32):
            numerical = disk_gravity_numerical(
                density,
                radius,
                (0.0, 0.0, center_z),
                (0.0, 0.0, 0.0),
                radial_cells=radial_cells,
                angular_cells=12,
            )[2]
            errors.append(abs(numerical - expected))
        self.assertGreater(errors[0], errors[1])
        self.assertGreater(errors[1], errors[2])
        self.assertLess(errors[2], errors[0] / 10.0)

    def test_invalid_grid_and_singular_plane_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            disk_gravity_numerical(1.0, 2.0, (0.0, 0.0, 0.0), (1.0, 0.0, 0.0))
        for radial_cells, angular_cells in ((0, 8), (8, 2), (True, 8)):
            with (
                self.subTest(radial_cells=radial_cells, angular_cells=angular_cells),
                self.assertRaises(ValueError),
            ):
                disk_gravity_numerical(
                    1.0,
                    2.0,
                    (0.0, 0.0, 0.0),
                    (0.0, 0.0, 1.0),
                    radial_cells=radial_cells,
                    angular_cells=angular_cells,
                )


if __name__ == "__main__":
    unittest.main()
