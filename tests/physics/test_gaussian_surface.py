"""Analytic, numerical, and limiting tests for Gaussian surface anomalies."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.gravity import (  # noqa: E402
    gaussian_surface_gravity_numerical,
    gaussian_vertical_gravity_on_axis,
    gravity_vector,
)


class TestGaussianSurfaceGravity(unittest.TestCase):
    def test_numerical_axis_matches_analytic_solution(self) -> None:
        density = 1_025.0
        scale = 1_000.0
        center_z = -800.0
        numerical = gaussian_surface_gravity_numerical(
            density,
            scale,
            (0.0, 0.0, center_z),
            (0.0, 0.0, 0.0),
            radial_cells=256,
            angular_cells=24,
        )
        analytic = gaussian_vertical_gravity_on_axis(density, scale, center_z, 0.0)
        self.assertLess(abs(numerical[2] - analytic) / abs(analytic), 5.0e-4)
        self.assertAlmostEqual(numerical[0], 0.0, delta=abs(analytic) * 1.0e-13)
        self.assertAlmostEqual(numerical[1], 0.0, delta=abs(analytic) * 1.0e-13)

    def test_far_field_matches_exact_total_mass(self) -> None:
        density = 3.0
        scale = 200.0
        separation = 100.0 * scale
        gaussian = gaussian_vertical_gravity_on_axis(density, scale, -separation, 0.0)
        total_mass = 2.0 * math.pi * density * scale**2
        point = gravity_vector(total_mass, (0.0, 0.0, -separation), (0.0, 0.0, 0.0))[2]
        self.assertLess(abs(gaussian - point) / abs(point), 0.01)

    def test_large_scale_approaches_infinite_sheet_limit(self) -> None:
        density = 10.0
        result = gaussian_vertical_gravity_on_axis(density, 1.0e10, -1.0, 0.0)
        expected_magnitude = 2.0 * math.pi * 6.67430e-11 * density
        self.assertAlmostEqual(result, -expected_magnitude, delta=expected_magnitude * 1.0e-9)

    def test_direction_and_signed_density(self) -> None:
        below = gaussian_vertical_gravity_on_axis(2.0, 3.0, 0.0, -4.0)
        above = gaussian_vertical_gravity_on_axis(2.0, 3.0, 0.0, 4.0)
        negative = gaussian_vertical_gravity_on_axis(-2.0, 3.0, 0.0, -4.0)
        self.assertGreater(below, 0.0)
        self.assertAlmostEqual(below, -above)
        self.assertAlmostEqual(negative, -below)

    def test_radial_refinement_reduces_axis_error(self) -> None:
        expected = gaussian_vertical_gravity_on_axis(1.0, 2.0, -1.0, 0.0)
        errors = []
        for radial_cells in (32, 64, 128):
            result = gaussian_surface_gravity_numerical(
                1.0,
                2.0,
                (0.0, 0.0, -1.0),
                (0.0, 0.0, 0.0),
                radial_cells=radial_cells,
                angular_cells=12,
            )[2]
            errors.append(abs(result - expected))
        self.assertGreater(errors[0], errors[1])
        self.assertGreater(errors[1], errors[2])
        self.assertLess(errors[2], errors[0] / 10.0)

    def test_cutoff_mass_fraction_is_negligible(self) -> None:
        omitted_fraction = math.exp(-0.5 * 8.0**2)
        self.assertLess(omitted_fraction, 1.0e-13)

    def test_plane_scale_and_grid_validation(self) -> None:
        with self.assertRaises(ValueError):
            gaussian_vertical_gravity_on_axis(1.0, 0.0, -1.0, 0.0)
        with self.assertRaises(ValueError):
            gaussian_vertical_gravity_on_axis(1.0, 1.0, 0.0, 0.0)
        with self.assertRaises(ValueError):
            gaussian_surface_gravity_numerical(
                1.0,
                1.0,
                (0.0, 0.0, -1.0),
                (0.0, 0.0, 0.0),
                radial_cells=0,
            )


if __name__ == "__main__":
    unittest.main()

