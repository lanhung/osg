"""Analytic, numerical, and limiting-case tests for rectangular surface loads."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.constants import GRAVITATIONAL_CONSTANT  # noqa: E402
from oceangravity.gravity import (  # noqa: E402
    gravity_vector,
    rectangle_gravity_numerical,
    rectangle_vertical_gravity_on_axis,
)


class TestRectangleGravity(unittest.TestCase):
    def test_numerical_axis_matches_analytic_solution(self) -> None:
        density = 1_025.0
        half_x = 2_000.0
        half_y = 1_000.0
        center_z = -800.0
        numerical = rectangle_gravity_numerical(
            density,
            half_x,
            half_y,
            (0.0, 0.0, center_z),
            (0.0, 0.0, 0.0),
            cells_x=128,
            cells_y=96,
        )
        analytic = rectangle_vertical_gravity_on_axis(
            density, half_x, half_y, center_z, 0.0
        )
        self.assertLess(abs(numerical[2] - analytic) / abs(analytic), 1.0e-4)
        self.assertAlmostEqual(numerical[0], 0.0, delta=abs(analytic) * 1.0e-14)
        self.assertAlmostEqual(numerical[1], 0.0, delta=abs(analytic) * 1.0e-14)

    def test_half_width_exchange_symmetry(self) -> None:
        first = rectangle_vertical_gravity_on_axis(2.0, 3.0, 7.0, -5.0, 0.0)
        second = rectangle_vertical_gravity_on_axis(2.0, 7.0, 3.0, -5.0, 0.0)
        self.assertEqual(first, second)

    def test_field_direction_on_both_sides(self) -> None:
        below = rectangle_vertical_gravity_on_axis(1.0, 2.0, 3.0, 0.0, -4.0)
        above = rectangle_vertical_gravity_on_axis(1.0, 2.0, 3.0, 0.0, 4.0)
        self.assertGreater(below, 0.0)
        self.assertLess(above, 0.0)
        self.assertAlmostEqual(below, -above)

    def test_far_field_matches_equal_point_mass(self) -> None:
        density = 1_025.0
        half_x = 100.0
        half_y = 50.0
        separation = 100.0 * max(half_x, half_y)
        rectangle = rectangle_vertical_gravity_on_axis(
            density, half_x, half_y, -separation, 0.0
        )
        mass = 4.0 * half_x * half_y * density
        point = gravity_vector(mass, (0.0, 0.0, -separation), (0.0, 0.0, 0.0))[2]
        self.assertLess(abs(rectangle - point) / abs(point), 0.01)

    def test_large_rectangle_approaches_infinite_sheet_limit(self) -> None:
        density = 1_025.0
        rectangle = rectangle_vertical_gravity_on_axis(
            density, 1.0e10, 1.0e10, -1.0, 0.0
        )
        expected = -2.0 * math.pi * GRAVITATIONAL_CONSTANT.value * density
        self.assertAlmostEqual(rectangle, expected, delta=abs(expected) * 1.0e-9)

    def test_numerical_refinement_reduces_axis_error(self) -> None:
        expected = rectangle_vertical_gravity_on_axis(1.0, 2.0, 1.0, -0.6, 0.0)
        errors = []
        for cells in (8, 16, 32):
            result = rectangle_gravity_numerical(
                1.0,
                2.0,
                1.0,
                (0.0, 0.0, -0.6),
                (0.0, 0.0, 0.0),
                cells_x=2 * cells,
                cells_y=cells,
            )[2]
            errors.append(abs(result - expected))
        self.assertGreater(errors[0], errors[1])
        self.assertGreater(errors[1], errors[2])
        self.assertLess(errors[2], errors[0] / 10.0)

    def test_off_axis_reflection_symmetry(self) -> None:
        kwargs = {"cells_x": 48, "cells_y": 36}
        positive_x = rectangle_gravity_numerical(
            3.0, 4.0, 2.0, (0.0, 0.0, -3.0), (6.0, 0.0, 1.0), **kwargs
        )
        negative_x = rectangle_gravity_numerical(
            3.0, 4.0, 2.0, (0.0, 0.0, -3.0), (-6.0, 0.0, 1.0), **kwargs
        )
        self.assertAlmostEqual(positive_x[0], -negative_x[0], delta=abs(positive_x[0]) * 1e-13)
        self.assertAlmostEqual(positive_x[2], negative_x[2], delta=abs(positive_x[2]) * 1e-13)

    def test_invalid_dimensions_grid_and_plane_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            rectangle_vertical_gravity_on_axis(1.0, 0.0, 1.0, -1.0, 0.0)
        with self.assertRaises(ValueError):
            rectangle_vertical_gravity_on_axis(1.0, 1.0, 1.0, 0.0, 0.0)
        with self.assertRaises(ValueError):
            rectangle_gravity_numerical(
                1.0, 1.0, 1.0, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)
            )
        with self.assertRaises(ValueError):
            rectangle_gravity_numerical(
                1.0,
                1.0,
                1.0,
                (0.0, 0.0, -1.0),
                (0.0, 0.0, 0.0),
                cells_x=True,
            )


if __name__ == "__main__":
    unittest.main()

