"""Provisional LoadDef normalization and combined-table adapter tests."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.loading import (
    LoadGreenFunctionMetadata,
    build_provisional_loaddef_combined_provider,
    convolve_combined_elastic_load_green_functions,
    loaddef_normalized_elastic_gravity_to_si,
)


def _metadata():
    return LoadGreenFunctionMetadata(
        provider_id="loaddef-test-only",
        provider_version="unverified",
        earth_model="test-only",
        source="unit-test fixture",
        component_semantics="combined_elastic_gravity",
        reference_frame="CE",
    )


class TestLoadDefAdapter(unittest.TestCase):
    def test_documented_normalization_round_trip(self) -> None:
        radius = 6_371_000.0
        theta = 0.25
        expected = -3.0e-19
        normalized = expected * 1.0e18 * radius * theta
        actual = loaddef_normalized_elastic_gravity_to_si(normalized, theta, radius)
        self.assertAlmostEqual(actual, expected)

    def test_degree_and_radian_tables_produce_same_provider(self) -> None:
        radius = 6_371_000.0
        angles_deg = (1.0, 2.0)
        angles_rad = tuple(math.radians(value) for value in angles_deg)
        physical = (2.0e-19, 4.0e-19)
        normalized = tuple(
            value * 1.0e18 * radius * angle
            for value, angle in zip(physical, angles_rad, strict=True)
        )
        degree_provider = build_provisional_loaddef_combined_provider(
            metadata=_metadata(),
            angular_distances=angles_deg,
            angular_distance_unit="deg",
            normalized_gE=normalized,
            radial_displacement_m_per_kg=(1.0e-12, 2.0e-12),
            earth_radius_m=radius,
        )
        radian_provider = build_provisional_loaddef_combined_provider(
            metadata=_metadata(),
            angular_distances=angles_rad,
            angular_distance_unit="rad",
            normalized_gE=normalized,
            radial_displacement_m_per_kg=(1.0e-12, 2.0e-12),
            earth_radius_m=radius,
        )
        self.assertEqual(degree_provider.angular_distances_rad, angles_rad)
        self.assertEqual(degree_provider.samples, radian_provider.samples)
        response = convolve_combined_elastic_load_green_functions(
            [5.0],
            [angles_rad[0]],
            degree_provider,
            direct_attraction_m_s2=7.0,
        )
        self.assertAlmostEqual(response.combined_elastic_gravity_m_s2, 1.0e-18)

    def test_zero_angle_and_ambiguous_inputs_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            loaddef_normalized_elastic_gravity_to_si(1.0, 0.0, 6_371_000.0)
        with self.assertRaises(ValueError):
            build_provisional_loaddef_combined_provider(
                metadata=_metadata(),
                angular_distances=(1.0, 2.0),
                angular_distance_unit="unknown",
                normalized_gE=(1.0, 2.0),
                radial_displacement_m_per_kg=(1.0, 2.0),
                earth_radius_m=6_371_000.0,
            )
        decomposed = LoadGreenFunctionMetadata(
            "fixture", "1", "test", "fixture", reference_frame="CE"
        )
        with self.assertRaisesRegex(ValueError, "combined semantics"):
            build_provisional_loaddef_combined_provider(
                metadata=decomposed,
                angular_distances=(1.0, 2.0),
                angular_distance_unit="deg",
                normalized_gE=(1.0, 2.0),
                radial_displacement_m_per_kg=(1.0, 2.0),
                earth_radius_m=6_371_000.0,
            )


if __name__ == "__main__":
    unittest.main()
