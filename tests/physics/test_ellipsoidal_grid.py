"""WGS 84 area, geometry, and spherical-sensitivity tests."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.constants import (  # noqa: E402
    WGS84_INVERSE_FLATTENING,
    WGS84_SEMI_MAJOR_AXIS,
)
from oceangravity.loading import (  # noqa: E402
    surface_load_gravity_spherical,
    surface_load_gravity_wgs84,
)


def _edges(start: float, stop: float, cells: int) -> list[float]:
    return [start + (stop - start) * index / cells for index in range(cells + 1)]


class TestEllipsoidalSurfaceGrid(unittest.TestCase):
    def test_global_area_matches_oblate_spheroid_formula(self) -> None:
        semi_major = WGS84_SEMI_MAJOR_AXIS.value
        flattening = 1.0 / WGS84_INVERSE_FLATTENING.value
        semi_minor = semi_major * (1.0 - flattening)
        eccentricity = math.sqrt(1.0 - (semi_minor / semi_major) ** 2)
        expected_area = 2.0 * math.pi * semi_major**2 * (
            1.0 + (1.0 - eccentricity**2) * math.atanh(eccentricity) / eccentricity
        )
        result = surface_load_gravity_wgs84(
            [[0.0] * 36 for _ in range(18)],
            _edges(-90.0, 90.0, 18),
            _edges(-180.0, 180.0, 36),
            0.0,
            0.0,
            1_000.0,
        )
        self.assertAlmostEqual(
            result.included_area_m2,
            expected_area,
            delta=expected_area * 3e-15,
        )

    def test_regional_patch_quantifies_sphere_ellipsoid_difference(self) -> None:
        cells = 20
        latitude_edges = _edges(18.0, 22.0, cells)
        longitude_edges = _edges(108.0, 112.0, cells)
        density = [[1_025.0] * cells for _ in range(cells)]
        ellipsoid = surface_load_gravity_wgs84(
            density,
            latitude_edges,
            longitude_edges,
            20.0,
            110.0,
            100_000.0,
        )
        sphere = surface_load_gravity_spherical(
            density,
            latitude_edges,
            longitude_edges,
            20.0,
            110.0,
            100_000.0,
        )
        relative = abs(
            ellipsoid.geodetic_up_gravity_m_s2 - sphere.radial_gravity_m_s2
        ) / abs(ellipsoid.geodetic_up_gravity_m_s2)
        self.assertLess(relative, 0.01)
        self.assertGreater(relative, 0.0)

    def test_load_height_is_explicit_and_changes_attraction(self) -> None:
        arguments = ([[1_025.0]], [19.0, 21.0], [109.0, 111.0], 20.0, 110.0, 100_000.0)
        sea_level = surface_load_gravity_wgs84(*arguments, load_height_m=0.0)
        elevated = surface_load_gravity_wgs84(*arguments, load_height_m=1_000.0)
        self.assertNotEqual(
            sea_level.geodetic_up_gravity_m_s2,
            elevated.geodetic_up_gravity_m_s2,
        )

    def test_mask_missing_and_validation_accounting(self) -> None:
        result = surface_load_gravity_wgs84(
            [[1.0, None, 3.0]],
            [-1.0, 1.0],
            [0.0, 1.0, 2.0, 3.0],
            10.0,
            20.0,
            1_000.0,
            water_mask=[[True, True, False]],
            missing_policy="skip",
        )
        self.assertEqual(result.included_cells, 1)
        self.assertEqual(result.skipped_missing_cells, 1)
        self.assertEqual(result.skipped_masked_cells, 1)
        with self.assertRaises(ValueError):
            surface_load_gravity_wgs84(
                [[1.0]], [-91.0, 0.0], [0.0, 1.0], 0.0, 0.0, 1_000.0
            )

    def test_geodetic_up_gradient_matches_height_finite_difference(self) -> None:
        arguments = ([[1_025.0]], [19.0, 21.0], [109.0, 111.0], 20.0, 110.0)
        step = 10.0
        lower = surface_load_gravity_wgs84(*arguments, 100_000.0 - step)
        centre = surface_load_gravity_wgs84(*arguments, 100_000.0)
        upper = surface_load_gravity_wgs84(*arguments, 100_000.0 + step)
        finite_difference = (
            upper.geodetic_up_gravity_m_s2 - lower.geodetic_up_gravity_m_s2
        ) / (2.0 * step)
        self.assertAlmostEqual(
            centre.geodetic_up_gravity_gradient_s2,
            finite_difference,
            delta=abs(finite_difference) * 2e-7,
        )
        tensor = centre.gravity_gradient_ecef_s2
        self.assertAlmostEqual(tensor[0][2], tensor[2][0])
        self.assertAlmostEqual(sum(tensor[index][index] for index in range(3)), 0.0)


if __name__ == "__main__":
    unittest.main()
