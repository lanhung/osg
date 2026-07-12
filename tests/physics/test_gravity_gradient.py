"""Analytic and finite-difference tests for gravity-gradient tensors."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.constants import GRAVITATIONAL_CONSTANT  # noqa: E402
from oceangravity.gravity import (  # noqa: E402
    gravity_gradient_tensor,
    gravity_vector,
    volume_cell_gravity_gradient,
)


class TestGravityGradient(unittest.TestCase):
    def test_axis_aligned_eigenvalues_and_trace(self) -> None:
        mass = 2.0e12
        distance = 3_000.0
        tensor = gravity_gradient_tensor(mass, (0.0, 0.0, -distance), (0.0, 0.0, 0.0))
        base = GRAVITATIONAL_CONSTANT.value * mass / distance**3
        expected = ((-base, 0.0, 0.0), (0.0, -base, 0.0), (0.0, 0.0, 2.0 * base))
        for row in range(3):
            for column in range(3):
                self.assertAlmostEqual(
                    tensor[row][column],
                    expected[row][column],
                    delta=base * 1.0e-15,
                )
        self.assertAlmostEqual(sum(tensor[index][index] for index in range(3)), 0.0)

    def test_tensor_is_symmetric_and_trace_free(self) -> None:
        tensor = gravity_gradient_tensor(9.0e8, (2.0, -3.0, 7.0), (-11.0, 5.0, 13.0))
        scale = max(abs(value) for row in tensor for value in row)
        for row in range(3):
            for column in range(3):
                self.assertEqual(tensor[row][column], tensor[column][row])
        self.assertAlmostEqual(
            sum(tensor[index][index] for index in range(3)),
            0.0,
            delta=scale * 2.0e-15,
        )

    def test_matches_central_finite_difference_of_acceleration(self) -> None:
        mass = 4.0e10
        source = (120.0, -80.0, -300.0)
        observation = (10.0, 20.0, 30.0)
        tensor = gravity_gradient_tensor(mass, source, observation)
        distance = math.dist(source, observation)
        step = distance * 1.0e-4
        for column in range(3):
            plus = list(observation)
            minus = list(observation)
            plus[column] += step
            minus[column] -= step
            acceleration_plus = gravity_vector(mass, source, plus)
            acceleration_minus = gravity_vector(mass, source, minus)
            for row in range(3):
                finite_difference = (
                    acceleration_plus[row] - acceleration_minus[row]
                ) / (2.0 * step)
                tolerance = max(abs(tensor[row][column]), 1.0e-30) * 1.0e-6
                self.assertAlmostEqual(
                    finite_difference,
                    tensor[row][column],
                    delta=tolerance,
                )

    def test_inverse_cube_scaling(self) -> None:
        near = gravity_gradient_tensor(
            1.0e10, (0.0, 0.0, -10.0), (0.0, 0.0, 0.0)
        )[2][2]
        far = gravity_gradient_tensor(
            1.0e10, (0.0, 0.0, -20.0), (0.0, 0.0, 0.0)
        )[2][2]
        self.assertAlmostEqual(near / far, 8.0)

    def test_negative_mass_reverses_tensor(self) -> None:
        positive = gravity_gradient_tensor(3.0, (1.0, 2.0, 3.0), (4.0, 5.0, 6.0))
        negative = gravity_gradient_tensor(-3.0, (1.0, 2.0, 3.0), (4.0, 5.0, 6.0))
        for row in range(3):
            self.assertEqual(negative[row], tuple(-value for value in positive[row]))

    def test_volume_cell_gradient_equals_sum_of_point_tensors(self) -> None:
        densities = [2.0, -3.0]
        centers = [(1.0, 2.0, -3.0), (-4.0, 5.0, -6.0)]
        volumes = [7.0, 11.0]
        observation = (20.0, 30.0, 40.0)
        combined = volume_cell_gravity_gradient(densities, centers, volumes, observation)
        first = gravity_gradient_tensor(densities[0] * volumes[0], centers[0], observation)
        second = gravity_gradient_tensor(densities[1] * volumes[1], centers[1], observation)
        for row in range(3):
            for column in range(3):
                expected = math.fsum((first[row][column], second[row][column]))
                self.assertEqual(combined[row][column], expected)

    def test_zero_mass_and_invalid_coincidence(self) -> None:
        zero = gravity_gradient_tensor(0.0, (1.0, 0.0, 0.0), (0.0, 0.0, 0.0))
        self.assertEqual(zero, ((0.0, 0.0, 0.0),) * 3)
        with self.assertRaisesRegex(ValueError, "singular"):
            gravity_gradient_tensor(1.0, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))


if __name__ == "__main__":
    unittest.main()

