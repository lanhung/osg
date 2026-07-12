"""Mass accounting and physics tests for local planar surface-load grids."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.gravity import (
    gravity_vector,
    rectangle_vertical_gravity_on_axis,
)
from oceangravity.loading import (
    sea_level_to_surface_density,
    surface_load_gravity_planar,
)


def _uniform_edges(half_width: float, cells: int) -> list[float]:
    return [-half_width + 2.0 * half_width * index / cells for index in range(cells + 1)]


class TestSurfaceGrid(unittest.TestCase):
    def test_sea_level_conversion_preserves_sign_and_missingness(self) -> None:
        result = sea_level_to_surface_density([[2.0, -0.5, None, math.nan]], 1_025.0)
        self.assertEqual(result, ((2_050.0, -512.5, None, None),))

    def test_single_cell_equals_centroid_point_mass_and_accounts_area(self) -> None:
        result = surface_load_gravity_planar(
            [[10.0]],
            [0.0, 2.0],
            [0.0, 3.0],
            -4.0,
            (10.0, 20.0, 30.0),
        )
        point = gravity_vector(60.0, (1.0, 1.5, -4.0), (10.0, 20.0, 30.0))
        self.assertEqual(result.gravity_m_s2, point)
        self.assertEqual(result.included_area_m2, 6.0)
        self.assertEqual(result.included_mass_kg, 60.0)
        self.assertEqual(result.included_cells, 1)

    def test_symmetric_grid_cancels_horizontal_gravity(self) -> None:
        result = surface_load_gravity_planar(
            [[1.0, 1.0], [1.0, 1.0]],
            [-1.0, 0.0, 1.0],
            [-1.0, 0.0, 1.0],
            -2.0,
            (0.0, 0.0, 0.0),
        )
        self.assertEqual(result.gravity_m_s2[0], 0.0)
        self.assertEqual(result.gravity_m_s2[1], 0.0)
        self.assertLess(result.gravity_m_s2[2], 0.0)

    def test_mask_and_missing_skip_are_audited(self) -> None:
        result = surface_load_gravity_planar(
            [[1.0, None], [3.0, 4.0]],
            [0.0, 1.0, 3.0],
            [0.0, 2.0, 5.0],
            -1.0,
            (10.0, 10.0, 10.0),
            water_mask=[[True, True], [False, True]],
            missing_policy="skip",
        )
        self.assertEqual(result.included_cells, 2)
        self.assertEqual(result.skipped_missing_cells, 1)
        self.assertEqual(result.skipped_masked_cells, 1)
        self.assertEqual(result.included_area_m2, 2.0 + 6.0)
        self.assertEqual(result.included_mass_kg, 2.0 + 24.0)

    def test_grid_refinement_converges_to_finite_rectangle(self) -> None:
        density = 1_025.0
        half_x = 2_000.0
        half_y = 1_000.0
        load_z = -800.0
        expected = rectangle_vertical_gravity_on_axis(density, half_x, half_y, load_z, 0.0)
        errors = []
        for cells_y in (4, 8, 16):
            cells_x = 2 * cells_y
            result = surface_load_gravity_planar(
                [[density] * cells_x for _ in range(cells_y)],
                _uniform_edges(half_x, cells_x),
                _uniform_edges(half_y, cells_y),
                load_z,
                (0.0, 0.0, 0.0),
            )
            errors.append(abs(result.gravity_m_s2[2] - expected))
        self.assertGreater(errors[0], errors[1])
        self.assertGreater(errors[1], errors[2])
        self.assertLess(errors[2], errors[0] / 10.0)
        self.assertLess(errors[2] / abs(expected), 0.01)

    def test_missing_error_and_invalid_shapes_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "missing"):
            surface_load_gravity_planar([[None]], [0.0, 1.0], [0.0, 1.0], -1.0, (0.0, 0.0, 0.0))
        with self.assertRaisesRegex(ValueError, "rectangular"):
            surface_load_gravity_planar(
                [[1.0], [1.0, 2.0]],
                [0.0, 1.0],
                [0.0, 1.0, 2.0],
                -1.0,
                (0.0, 0.0, 0.0),
            )
        with self.assertRaisesRegex(ValueError, "strictly increasing"):
            surface_load_gravity_planar([[1.0]], [0.0, 0.0], [0.0, 1.0], -1.0, (0.0, 0.0, 0.0))

    def test_nonzero_centroid_at_observer_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "refine"):
            surface_load_gravity_planar([[1.0]], [-1.0, 1.0], [-1.0, 1.0], 0.0, (0.0, 0.0, 0.0))


if __name__ == "__main__":
    unittest.main()
