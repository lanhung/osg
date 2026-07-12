"""Mass closure, spatial convergence, and domain-truncation tests for loads."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.loading import surface_load_gravity_spherical


def _edges(start: float, stop: float, cells: int) -> list[float]:
    return [start + (stop - start) * index / cells for index in range(cells + 1)]


def _gaussian_grid(half_width_deg: float, cells: int, sigma_deg: float = 1.0) -> list[list[float]]:
    edges = _edges(-half_width_deg, half_width_deg, cells)
    values = []
    for row in range(cells):
        latitude = 0.5 * (edges[row] + edges[row + 1])
        values.append(
            [
                math.exp(
                    -0.5
                    * (latitude**2 + (0.5 * (edges[column] + edges[column + 1])) ** 2)
                    / sigma_deg**2
                )
                for column in range(cells)
            ]
        )
    return values


def _gaussian_response(half_width_deg: float, cells: int) -> float:
    edges = _edges(-half_width_deg, half_width_deg, cells)
    result = surface_load_gravity_spherical(
        _gaussian_grid(half_width_deg, cells),
        edges,
        edges,
        0.0,
        0.0,
        100_000.0,
        chunk_size_cells=128,
    )
    return result.radial_gravity_m_s2


class TestLoadingConvergence(unittest.TestCase):
    def test_signed_symmetric_load_has_zero_total_mass(self) -> None:
        result = surface_load_gravity_spherical(
            [[1.0, -1.0], [1.0, -1.0]],
            [-2.0, 0.0, 2.0],
            [-2.0, 0.0, 2.0],
            10.0,
            20.0,
            100_000.0,
        )
        self.assertAlmostEqual(
            result.included_mass_kg,
            0.0,
            delta=result.included_area_m2 * 2e-15,
        )

    def test_grid_refinement_reduces_error_against_fine_reference(self) -> None:
        coarse = _gaussian_response(4.0, 16)
        medium = _gaussian_response(4.0, 32)
        fine = _gaussian_response(4.0, 64)
        self.assertLess(abs(medium - fine), abs(coarse - fine))
        self.assertLess(abs(medium - fine) / abs(fine), 0.02)

    def test_domain_truncation_converges_for_localized_load(self) -> None:
        # Keep approximately 0.125-degree cells as the domain expands.
        narrow = _gaussian_response(2.0, 32)
        medium = _gaussian_response(4.0, 64)
        wide = _gaussian_response(6.0, 96)
        self.assertLess(abs(medium - wide), abs(narrow - wide))
        self.assertLess(abs(medium - wide) / abs(wide), 0.01)


if __name__ == "__main__":
    unittest.main()
