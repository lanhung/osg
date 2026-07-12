"""Physics tests for discretized three-dimensional density anomalies."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.gravity import gravity_vector, volume_cell_gravity


class TestVolumeCellGravity(unittest.TestCase):
    def test_single_cell_equals_point_mass(self) -> None:
        density = 2_000.0
        volume = 30.0
        center = (1.0, 2.0, -3.0)
        observation = (5.0, -7.0, 11.0)
        cell = volume_cell_gravity([density], [center], volume, observation)
        point = gravity_vector(density * volume, center, observation)
        for cell_component, point_component in zip(cell, point, strict=True):
            self.assertAlmostEqual(
                cell_component,
                point_component,
                delta=abs(point_component) * 2.0e-15,
            )

    def test_symmetric_pair_cancels_horizontal_components(self) -> None:
        result = volume_cell_gravity(
            [10.0, 10.0],
            [(-2.0, 0.0, -3.0), (2.0, 0.0, -3.0)],
            [4.0, 4.0],
            (0.0, 0.0, 0.0),
        )
        self.assertEqual(result[0], 0.0)
        self.assertEqual(result[1], 0.0)
        self.assertLess(result[2], 0.0)

    def test_equal_opposite_anomalies_cancel(self) -> None:
        result = volume_cell_gravity(
            [7.0, -7.0],
            [(3.0, 4.0, 5.0), (3.0, 4.0, 5.0)],
            2.0,
            (0.0, 0.0, 0.0),
        )
        self.assertEqual(result, (0.0, 0.0, 0.0))

    def test_translation_invariance(self) -> None:
        densities = [1.0, -2.0, 3.0]
        centers = [(1.0, 2.0, 3.0), (-4.0, 5.0, -6.0), (7.0, -8.0, 9.0)]
        observation = (10.0, 11.0, 12.0)
        shift = (100.0, -200.0, 300.0)
        shifted_centers = [
            tuple(center[index] + shift[index] for index in range(3)) for center in centers
        ]
        shifted_observation = tuple(observation[index] + shift[index] for index in range(3))
        first = volume_cell_gravity(densities, centers, [2.0, 4.0, 6.0], observation)
        second = volume_cell_gravity(
            densities, shifted_centers, [2.0, 4.0, 6.0], shifted_observation
        )
        self.assertEqual(first, second)

    def test_gaussian_grid_far_field_matches_exact_total_mass(self) -> None:
        peak_density = 5.0
        scale = 100.0
        cells_per_axis = 20
        step = 0.4 * scale
        coordinates = [
            (-0.5 * cells_per_axis + index + 0.5) * step for index in range(cells_per_axis)
        ]
        densities = []
        centers = []
        for x in coordinates:
            for y in coordinates:
                for z in coordinates:
                    centers.append((x, y, z))
                    densities.append(
                        peak_density * math.exp(-(x**2 + y**2 + z**2) / (2.0 * scale**2))
                    )
        observation = (0.0, 0.0, 20.0 * scale)
        numerical = volume_cell_gravity(densities, centers, step**3, observation)
        exact_total_mass = (2.0 * math.pi) ** 1.5 * peak_density * scale**3
        point = gravity_vector(exact_total_mass, (0.0, 0.0, 0.0), observation)
        self.assertLess(abs(numerical[2] - point[2]) / abs(point[2]), 0.01)
        self.assertAlmostEqual(numerical[0], 0.0, delta=abs(point[2]) * 1.0e-14)
        self.assertAlmostEqual(numerical[1], 0.0, delta=abs(point[2]) * 1.0e-14)

    def test_zero_density_at_observation_is_safe(self) -> None:
        result = volume_cell_gravity([0.0], [(0.0, 0.0, 0.0)], 1.0, (0.0, 0.0, 0.0))
        self.assertEqual(result, (0.0, 0.0, 0.0))

    def test_nonzero_cell_at_observation_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "refine"):
            volume_cell_gravity([1.0], [(0.0, 0.0, 0.0)], 1.0, (0.0, 0.0, 0.0))

    def test_shape_and_volume_validation(self) -> None:
        with self.assertRaises(ValueError):
            volume_cell_gravity([1.0], [], 1.0, (0.0, 0.0, 0.0))
        with self.assertRaises(ValueError):
            volume_cell_gravity([1.0], [(1.0, 0.0, 0.0)], 0.0, (0.0, 0.0, 0.0))
        with self.assertRaises(ValueError):
            volume_cell_gravity([1.0], [(1.0, 0.0, 0.0)], [], (0.0, 0.0, 0.0))


if __name__ == "__main__":
    unittest.main()
