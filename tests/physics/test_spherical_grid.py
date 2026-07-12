"""Geometry and shell-theorem tests for spherical surface-load grids."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.constants import MEAN_EARTH_RADIUS  # noqa: E402
from oceangravity.gravity import gravity_vector  # noqa: E402
from oceangravity.loading import (  # noqa: E402
    surface_load_gravity_planar,
    surface_load_gravity_spherical,
)


def _uniform_edges(start: float, stop: float, cells: int) -> list[float]:
    return [start + (stop - start) * index / cells for index in range(cells + 1)]


class TestSphericalSurfaceGrid(unittest.TestCase):
    def test_global_grid_area_closes_to_sphere(self) -> None:
        radius = MEAN_EARTH_RADIUS.value
        latitude_edges = _uniform_edges(-90.0, 90.0, 18)
        longitude_edges = _uniform_edges(-180.0, 180.0, 36)
        result = surface_load_gravity_spherical(
            [[1.0] * 36 for _ in range(18)],
            latitude_edges,
            longitude_edges,
            0.0,
            0.0,
            radius,
        )
        expected_area = 4.0 * math.pi * radius**2
        self.assertAlmostEqual(
            result.included_area_m2,
            expected_area,
            delta=expected_area * 2.0e-15,
        )
        self.assertAlmostEqual(result.included_mass_kg, expected_area, delta=expected_area * 2e-15)

    def test_uniform_shell_matches_central_point_mass_outside(self) -> None:
        radius = MEAN_EARTH_RADIUS.value
        density = 2.0
        lat_cells = 36
        lon_cells = 72
        result = surface_load_gravity_spherical(
            [[density] * lon_cells for _ in range(lat_cells)],
            _uniform_edges(-90.0, 90.0, lat_cells),
            _uniform_edges(-180.0, 180.0, lon_cells),
            0.0,
            0.0,
            radius,
        )
        total_mass = 4.0 * math.pi * radius**2 * density
        point = gravity_vector(total_mass, (0.0, 0.0, 0.0), (2.0 * radius, 0.0, 0.0))
        self.assertLess(abs(result.radial_gravity_m_s2 - point[0]) / abs(point[0]), 0.01)
        self.assertAlmostEqual(result.gravity_ecef_m_s2[1], 0.0, delta=abs(point[0]) * 1e-14)
        self.assertAlmostEqual(result.gravity_ecef_m_s2[2], 0.0, delta=abs(point[0]) * 1e-14)

    def test_antimeridian_unwrapped_longitudes_are_invariant(self) -> None:
        first = surface_load_gravity_spherical(
            [[3.0, 4.0]],
            [-1.0, 1.0],
            [170.0, 180.0, 190.0],
            0.0,
            180.0,
            100_000.0,
        )
        second = surface_load_gravity_spherical(
            [[3.0, 4.0]],
            [-1.0, 1.0],
            [-190.0, -180.0, -170.0],
            0.0,
            -180.0,
            100_000.0,
        )
        for first_component, second_component in zip(
            first.gravity_ecef_m_s2, second.gravity_ecef_m_s2, strict=True
        ):
            self.assertAlmostEqual(
                first_component,
                second_component,
                delta=max(abs(first_component), 1e-30) * 2e-14,
            )

    def test_small_patch_agrees_with_local_planar_limit(self) -> None:
        radius = MEAN_EARTH_RADIUS.value
        angular_half_width = 0.1
        cells = 20
        height = 100_000.0
        density = 1_025.0
        angle_edges = _uniform_edges(-angular_half_width, angular_half_width, cells)
        spherical = surface_load_gravity_spherical(
            [[density] * cells for _ in range(cells)],
            angle_edges,
            angle_edges,
            0.0,
            0.0,
            height,
        )
        metres_per_degree = math.pi * radius / 180.0
        planar_edges = [edge * metres_per_degree for edge in angle_edges]
        planar = surface_load_gravity_planar(
            [[density] * cells for _ in range(cells)],
            planar_edges,
            planar_edges,
            0.0,
            (0.0, 0.0, height),
        )
        relative_difference = abs(
            spherical.radial_gravity_m_s2 - planar.gravity_m_s2[2]
        ) / abs(planar.gravity_m_s2[2])
        self.assertLess(relative_difference, 0.01)

    def test_mask_missing_and_geometry_validation(self) -> None:
        result = surface_load_gravity_spherical(
            [[1.0, None]],
            [-1.0, 1.0],
            [0.0, 1.0, 2.0],
            10.0,
            20.0,
            1_000.0,
            missing_policy="skip",
        )
        self.assertEqual(result.included_cells, 1)
        self.assertEqual(result.skipped_missing_cells, 1)
        with self.assertRaises(ValueError):
            surface_load_gravity_spherical(
                [[1.0]],
                [-91.0, 0.0],
                [0.0, 1.0],
                0.0,
                0.0,
                1.0,
            )
        with self.assertRaises(ValueError):
            surface_load_gravity_spherical(
                [[1.0]],
                [-1.0, 1.0],
                [0.0, 361.0],
                0.0,
                0.0,
                1.0,
            )


if __name__ == "__main__":
    unittest.main()

