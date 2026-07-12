"""Analytic and limiting-case tests for point-mass gravity."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.constants import GRAVITATIONAL_CONSTANT  # noqa: E402
from oceangravity.gravity import gravity_vector, vertical_gravity  # noqa: E402


class TestPointMassGravity(unittest.TestCase):
    """Check Newton's analytic solution under the project coordinate convention."""

    def test_axis_aligned_magnitude_and_direction(self) -> None:
        mass = 4.2e12
        distance = 3_000.0
        result = gravity_vector(mass, (0.0, 0.0, -distance), (0.0, 0.0, 0.0))
        expected_z = -GRAVITATIONAL_CONSTANT.value * mass / distance**2
        self.assertEqual(result[0], 0.0)
        self.assertEqual(result[1], 0.0)
        self.assertAlmostEqual(result[2], expected_z, delta=abs(expected_z) * 1.0e-15)

    def test_general_vector_has_analytic_magnitude(self) -> None:
        mass = 8.5e9
        source = (2.0, -3.0, 6.0)
        observation = (-1.0, 1.0, -6.0)
        displacement = tuple(source[i] - observation[i] for i in range(3))
        distance = math.sqrt(sum(value * value for value in displacement))
        result = gravity_vector(mass, source, observation)
        magnitude = math.sqrt(sum(value * value for value in result))
        expected = GRAVITATIONAL_CONSTANT.value * mass / distance**2
        self.assertAlmostEqual(magnitude, expected, delta=expected * 1.0e-15)

    def test_inverse_square_scaling(self) -> None:
        near = abs(vertical_gravity(1.0e10, (0.0, 0.0, -10.0), (0.0, 0.0, 0.0)))
        far = abs(vertical_gravity(1.0e10, (0.0, 0.0, -20.0), (0.0, 0.0, 0.0)))
        self.assertAlmostEqual(near / far, 4.0)

    def test_translation_invariance(self) -> None:
        base = gravity_vector(1.0e8, (1.0, 2.0, 3.0), (4.0, 6.0, 8.0))
        shifted = gravity_vector(1.0e8, (11.0, -18.0, 33.0), (14.0, -14.0, 38.0))
        self.assertEqual(base, shifted)

    def test_negative_anomaly_reverses_direction(self) -> None:
        positive = gravity_vector(3.0, (1.0, 2.0, 3.0), (4.0, 5.0, 6.0))
        negative = gravity_vector(-3.0, (1.0, 2.0, 3.0), (4.0, 5.0, 6.0))
        self.assertEqual(negative, tuple(-value for value in positive))

    def test_zero_mass_returns_zero_away_from_source(self) -> None:
        self.assertEqual(
            gravity_vector(0.0, (1.0, 2.0, 3.0), (4.0, 5.0, 6.0)),
            (0.0, 0.0, 0.0),
        )

    def test_coincident_geometry_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "singular"):
            gravity_vector(1.0, (1.0, 2.0, 3.0), (1.0, 2.0, 3.0))

    def test_invalid_inputs_are_rejected(self) -> None:
        cases = (
            (math.inf, (0.0, 0.0, 0.0), (1.0, 0.0, 0.0)),
            (1.0, (math.nan, 0.0, 0.0), (1.0, 0.0, 0.0)),
            (1.0, (0.0, 0.0), (1.0, 0.0, 0.0)),
        )
        for mass, source, observation in cases:
            with self.subTest(mass=mass, source=source, observation=observation):
                with self.assertRaises(ValueError):
                    gravity_vector(mass, source, observation)


if __name__ == "__main__":
    unittest.main()

