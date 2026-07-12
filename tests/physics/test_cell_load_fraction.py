"""Partial coastal-cell area tests across planar, spherical, and WGS 84 grids."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.loading import (
    surface_load_gravity_planar,
    surface_load_gravity_spherical,
    surface_load_gravity_wgs84,
)


class TestCellLoadFraction(unittest.TestCase):
    def test_planar_partial_cell_scales_area_mass_and_gravity(self) -> None:
        arguments = ([[2.0]], [0.0, 10.0], [0.0, 10.0], 0.0, (5.0, 5.0, 10.0))
        full = surface_load_gravity_planar(*arguments)
        quarter = surface_load_gravity_planar(*arguments, cell_load_fraction=[[0.25]])
        self.assertEqual(quarter.included_area_m2, 25.0)
        self.assertEqual(quarter.included_mass_kg, 50.0)
        self.assertEqual(quarter.gravity_m_s2[2], 0.25 * full.gravity_m_s2[2])

    def test_spherical_and_ellipsoidal_partial_cells_scale_linearly(self) -> None:
        arguments = ([[2.0]], [-1.0, 1.0], [10.0, 12.0], 0.0, 11.0, 100_000.0)
        for kernel, gravity_name in (
            (surface_load_gravity_spherical, "radial_gravity_m_s2"),
            (surface_load_gravity_wgs84, "geodetic_up_gravity_m_s2"),
        ):
            full = kernel(*arguments)
            quarter = kernel(*arguments, cell_load_fraction=[[0.25]])
            self.assertAlmostEqual(quarter.included_area_m2, 0.25 * full.included_area_m2)
            self.assertAlmostEqual(quarter.included_mass_kg, 0.25 * full.included_mass_kg)
            self.assertAlmostEqual(
                getattr(quarter, gravity_name),
                0.25 * getattr(full, gravity_name),
            )

    def test_zero_fraction_skips_land_nan_without_missing_error(self) -> None:
        result = surface_load_gravity_planar(
            [[None]],
            [0.0, 1.0],
            [0.0, 1.0],
            0.0,
            (0.5, 0.5, 1.0),
            cell_load_fraction=[[0.0]],
        )
        self.assertEqual(result.skipped_zero_fraction_cells, 1)
        self.assertEqual(result.skipped_missing_cells, 0)
        self.assertEqual(result.included_cells, 0)

    def test_invalid_fraction_values_and_shapes_are_rejected(self) -> None:
        arguments = ([[1.0]], [0.0, 1.0], [0.0, 1.0], 0.0, (0.5, 0.5, 1.0))
        for fractions in ([[-0.1]], [[1.1]], [[0.5, 0.5]]):
            with self.assertRaises(ValueError):
                surface_load_gravity_planar(*arguments, cell_load_fraction=fractions)


if __name__ == "__main__":
    unittest.main()
