"""Demonstrate far-field suppression from compensated 3-D density anomalies."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.gravity import volume_cell_gravity


def _gaussian_pair_grid(
    *, peak_density: float, scale: float, vertical_offset: float
) -> tuple[list[float], list[tuple[float, float, float]], float, int]:
    """Build identical positive/negative Gaussian grids separated vertically."""

    cells_per_axis = 12
    step = 0.5 * scale
    coordinates = [(-0.5 * cells_per_axis + index + 0.5) * step for index in range(cells_per_axis)]
    densities: list[float] = []
    centers: list[tuple[float, float, float]] = []
    positive_count = 0
    for sign, centre_z in ((1.0, vertical_offset), (-1.0, -vertical_offset)):
        for x in coordinates:
            for y in coordinates:
                for local_z in coordinates:
                    density = peak_density * math.exp(
                        -(x**2 + y**2 + local_z**2) / (2.0 * scale**2)
                    )
                    centers.append((x, y, centre_z + local_z))
                    densities.append(sign * density)
                    if sign > 0.0:
                        positive_count += 1
    return densities, centers, step**3, positive_count


class TestDensityCompensation(unittest.TestCase):
    def test_compensated_pair_suppresses_monopole_and_has_dipole_decay(self) -> None:
        scale = 100.0
        densities, centers, cell_volume, positive_count = _gaussian_pair_grid(
            peak_density=5.0,
            scale=scale,
            vertical_offset=scale,
        )
        self.assertAlmostEqual(math.fsum(densities) * cell_volume, 0.0, delta=1.0e-6)

        near_observation = (0.0, 0.0, 20.0 * scale)
        far_observation = (0.0, 0.0, 40.0 * scale)
        compensated_near = volume_cell_gravity(densities, centers, cell_volume, near_observation)[2]
        compensated_far = volume_cell_gravity(densities, centers, cell_volume, far_observation)[2]

        positive_densities = densities[:positive_count]
        positive_centers = centers[:positive_count]
        uncompensated_near = volume_cell_gravity(
            positive_densities, positive_centers, cell_volume, near_observation
        )[2]
        uncompensated_far = volume_cell_gravity(
            positive_densities, positive_centers, cell_volume, far_observation
        )[2]

        compensated_distance_ratio = abs(compensated_near / compensated_far)
        uncompensated_distance_ratio = abs(uncompensated_near / uncompensated_far)
        self.assertGreater(compensated_distance_ratio, 6.0)
        self.assertLess(compensated_distance_ratio, 11.0)
        self.assertGreater(uncompensated_distance_ratio, 3.0)
        self.assertLess(uncompensated_distance_ratio, 5.5)
        self.assertLess(abs(compensated_near), 0.2 * abs(uncompensated_near))


if __name__ == "__main__":
    unittest.main()
