"""Contract and component-separation tests for load Green functions."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.loading import (  # noqa: E402
    LoadGreenFunctionMetadata,
    LoadGreenFunctionSample,
    convolve_load_green_functions,
)


class AnalyticFixtureProvider:
    metadata = LoadGreenFunctionMetadata(
        provider_id="analytic-fixture",
        provider_version="1",
        earth_model="not-a-physical-earth-model",
        source="unit-test fixture",
    )

    def evaluate(self, angular_distance_rad: float) -> LoadGreenFunctionSample:
        return LoadGreenFunctionSample(
            deformation_gravity_m_s2_per_kg=2.0 * angular_distance_rad,
            internal_mass_gravity_m_s2_per_kg=-0.5 * angular_distance_rad,
            vertical_displacement_m_per_kg=3.0 * angular_distance_rad,
        )


class TestLoadGreenFunctions(unittest.TestCase):
    def test_convolution_preserves_components_and_metadata(self) -> None:
        provider = AnalyticFixtureProvider()
        response = convolve_load_green_functions(
            [2.0, -1.0],
            [0.1, 0.2],
            provider,
            direct_attraction_m_s2=7.0,
        )
        weighted_distance = 2.0 * 0.1 - 1.0 * 0.2
        self.assertAlmostEqual(response.deformation_gravity_m_s2, 2.0 * weighted_distance)
        self.assertAlmostEqual(response.internal_mass_gravity_m_s2, -0.5 * weighted_distance)
        self.assertAlmostEqual(response.vertical_displacement_m, 3.0 * weighted_distance)
        self.assertEqual(response.direct_attraction_m_s2, 7.0)
        self.assertEqual(response.total_gravity_m_s2, 7.0)
        self.assertEqual(response.green_function_provider_id, "analytic-fixture")

    def test_total_gravity_is_only_the_three_documented_gravity_terms(self) -> None:
        response = convolve_load_green_functions(
            [1.0], [0.5], AnalyticFixtureProvider(), direct_attraction_m_s2=4.0
        )
        expected = math.fsum((4.0, 1.0, -0.25))
        self.assertEqual(response.total_gravity_m_s2, expected)
        self.assertNotEqual(response.total_gravity_m_s2, expected + response.vertical_displacement_m)

    def test_zero_mass_does_not_require_singular_provider_evaluation(self) -> None:
        response = convolve_load_green_functions(
            [0.0], [0.0], AnalyticFixtureProvider(), direct_attraction_m_s2=1.0
        )
        self.assertEqual(response.total_gravity_m_s2, 1.0)

    def test_invalid_shapes_angles_and_metadata_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            convolve_load_green_functions(
                [1.0], [], AnalyticFixtureProvider(), direct_attraction_m_s2=0.0
            )
        with self.assertRaises(ValueError):
            convolve_load_green_functions(
                [1.0], [math.pi + 0.1], AnalyticFixtureProvider(), direct_attraction_m_s2=0.0
            )
        with self.assertRaises(ValueError):
            LoadGreenFunctionMetadata("", "1", "earth", "source")
        with self.assertRaises(ValueError):
            LoadGreenFunctionMetadata("id", "1", "earth", "source", normalization="per-area")


if __name__ == "__main__":
    unittest.main()

