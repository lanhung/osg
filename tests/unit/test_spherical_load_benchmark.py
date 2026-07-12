"""Smoke tests for the spherical-load scaling benchmark harness."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from benchmark_spherical_load import benchmark_grid  # noqa: E402


class TestSphericalLoadBenchmark(unittest.TestCase):
    def test_small_benchmark_reports_all_cases_and_numerical_agreement(self) -> None:
        result = benchmark_grid(4, 8, (None, 3, 16))
        self.assertEqual(result["grid"]["total_cells"], 32)
        self.assertEqual(len(result["cases"]), 3)
        for case in result["cases"]:
            self.assertEqual(case["included_cells"], 32)
            self.assertGreater(case["integrator_peak_traced_bytes"], 0)
            self.assertLess(
                case["maximum_relative_gravity_difference_from_unchunked"], 2e-15
            )

    def test_invalid_grid_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            benchmark_grid(0, 8, (None,))


if __name__ == "__main__":
    unittest.main()
