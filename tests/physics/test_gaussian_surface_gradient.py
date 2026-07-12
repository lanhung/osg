"""Finite-difference and far-field validation for Gaussian surface Tzz."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.gravity import (
    gaussian_surface_gravity_numerical,
    gaussian_surface_response_numerical,
    gaussian_vertical_gravity_on_axis,
    gravity_gradient_tensor,
)


class TestGaussianSurfaceGradient(unittest.TestCase):
    def test_axis_gradient_matches_finite_difference_of_analytic_gravity(self) -> None:
        density = 1_025.0
        scale = 2_000.0
        anomaly_z = -1_000.0
        observation_z = 500.0
        step = 0.1
        finite_difference = (
            gaussian_vertical_gravity_on_axis(density, scale, anomaly_z, observation_z + step)
            - gaussian_vertical_gravity_on_axis(density, scale, anomaly_z, observation_z - step)
        ) / (2.0 * step)
        response = gaussian_surface_response_numerical(
            density,
            scale,
            (0.0, 0.0, anomaly_z),
            (0.0, 0.0, observation_z),
            radial_cells=512,
            angular_cells=16,
        )
        self.assertLess(
            abs(response.vertical_gravity_gradient_s2 - finite_difference) / abs(finite_difference),
            5e-4,
        )

    def test_off_axis_gradient_matches_numerical_gravity_difference(self) -> None:
        density = 10.0
        scale = 500.0
        center = (100.0, -200.0, -800.0)
        observation = (300.0, 400.0, 100.0)
        step = 0.1
        response = gaussian_surface_response_numerical(
            density,
            scale,
            center,
            observation,
            radial_cells=96,
            angular_cells=144,
        )
        plus = (observation[0], observation[1], observation[2] + step)
        minus = (observation[0], observation[1], observation[2] - step)
        finite_difference = (
            gaussian_surface_gravity_numerical(
                density, scale, center, plus, radial_cells=96, angular_cells=144
            )[2]
            - gaussian_surface_gravity_numerical(
                density, scale, center, minus, radial_cells=96, angular_cells=144
            )[2]
        ) / (2.0 * step)
        self.assertAlmostEqual(
            response.vertical_gravity_gradient_s2,
            finite_difference,
            delta=abs(finite_difference) * 2e-8,
        )

    def test_far_field_matches_exact_total_mass_point_gradient(self) -> None:
        density = 3.0
        scale = 100.0
        separation = 100.0 * scale
        response = gaussian_surface_response_numerical(
            density,
            scale,
            (0.0, 0.0, -separation),
            (0.0, 0.0, 0.0),
            radial_cells=64,
            angular_cells=24,
        )
        mass = 2.0 * math.pi * density * scale**2
        point = gravity_gradient_tensor(mass, (0.0, 0.0, -separation), (0.0, 0.0, 0.0))[2][2]
        self.assertLess(
            abs(response.vertical_gravity_gradient_s2 - point) / abs(point),
            0.01,
        )

    def test_sign_reverses_with_density(self) -> None:
        positive = gaussian_surface_response_numerical(
            1.0, 2.0, (0.0, 0.0, -3.0), (1.0, 0.0, 4.0), radial_cells=16, angular_cells=24
        )
        negative = gaussian_surface_response_numerical(
            -1.0, 2.0, (0.0, 0.0, -3.0), (1.0, 0.0, 4.0), radial_cells=16, angular_cells=24
        )
        self.assertEqual(
            negative.vertical_gravity_gradient_s2,
            -positive.vertical_gravity_gradient_s2,
        )


if __name__ == "__main__":
    unittest.main()
