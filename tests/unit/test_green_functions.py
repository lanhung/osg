"""Contract and component-separation tests for load Green functions."""

from __future__ import annotations

import math
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.loading import (  # noqa: E402
    CombinedElasticLoadGreenFunctionSample,
    LoadGreenFunctionMetadata,
    LoadGreenFunctionScientificAudit,
    LoadGreenFunctionSample,
    TabulatedLoadGreenFunctionProvider,
    assert_green_function_scientific_use_ready,
    convolve_combined_elastic_load_green_functions,
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


class CombinedFixtureProvider:
    metadata = LoadGreenFunctionMetadata(
        provider_id="combined-fixture",
        provider_version="1",
        earth_model="not-a-physical-earth-model",
        source="unit-test fixture",
        component_semantics="combined_elastic_gravity",
    )

    def evaluate(self, angular_distance_rad: float) -> CombinedElasticLoadGreenFunctionSample:
        return CombinedElasticLoadGreenFunctionSample(
            elastic_gravity_m_s2_per_kg=1.5 * angular_distance_rad,
            vertical_displacement_m_per_kg=-2.0 * angular_distance_rad,
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

    def test_tabulated_provider_interpolates_components_without_extrapolation(self) -> None:
        provider = TabulatedLoadGreenFunctionProvider(
            metadata=AnalyticFixtureProvider.metadata,
            angular_distances_rad=(0.1, 0.2, 0.5),
            samples=(
                LoadGreenFunctionSample(1.0, -2.0, 3.0),
                LoadGreenFunctionSample(2.0, -4.0, 6.0),
                LoadGreenFunctionSample(5.0, -10.0, 15.0),
            ),
        )
        self.assertEqual(provider.evaluate(0.1), provider.samples[0])
        self.assertEqual(provider.evaluate(0.5), provider.samples[-1])
        interpolated = provider.evaluate(0.35)
        for actual, expected in zip(interpolated.as_tuple(), (3.5, -7.0, 10.5), strict=True):
            self.assertAlmostEqual(actual, expected)
        with self.assertRaises(ValueError):
            provider.evaluate(0.09)
        with self.assertRaises(ValueError):
            provider.evaluate(0.51)

    def test_tabulated_provider_json_schema(self) -> None:
        document = {
            "schema_version": 1,
            "metadata": {
                "provider_id": "fixture",
                "provider_version": "1",
                "earth_model": "test-only",
                "source": "unit-test fixture",
                "normalization": "per_source_mass_kg",
            },
            "interpolation": "linear_angular_distance",
            "angular_distances_rad": [0.0, 1.0],
            "deformation_gravity_m_s2_per_kg": [0.0, 1.0],
            "internal_mass_gravity_m_s2_per_kg": [0.0, -1.0],
            "vertical_displacement_m_per_kg": [0.0, 2.0],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            provider = TabulatedLoadGreenFunctionProvider.from_json(path)
        self.assertEqual(provider.evaluate(0.25), LoadGreenFunctionSample(0.25, -0.25, 0.5))

    def test_tabulated_provider_rejects_bad_tables(self) -> None:
        with self.assertRaises(ValueError):
            TabulatedLoadGreenFunctionProvider(
                metadata=AnalyticFixtureProvider.metadata,
                angular_distances_rad=(0.2, 0.1),
                samples=(
                    LoadGreenFunctionSample(0.0, 0.0, 0.0),
                    LoadGreenFunctionSample(0.0, 0.0, 0.0),
                ),
            )

    def test_combined_elastic_output_is_preserved_without_fake_split(self) -> None:
        response = convolve_combined_elastic_load_green_functions(
            [2.0, 1.0],
            [0.1, 0.2],
            CombinedFixtureProvider(),
            direct_attraction_m_s2=4.0,
        )
        weighted_distance = 2.0 * 0.1 + 1.0 * 0.2
        self.assertAlmostEqual(
            response.combined_elastic_gravity_m_s2, 1.5 * weighted_distance
        )
        self.assertAlmostEqual(response.vertical_displacement_m, -2.0 * weighted_distance)
        self.assertAlmostEqual(
            response.total_gravity_m_s2, 4.0 + 1.5 * weighted_distance
        )
        self.assertFalse(hasattr(response, "deformation_gravity_m_s2"))
        self.assertFalse(hasattr(response, "internal_mass_gravity_m_s2"))

    def test_component_semantics_cannot_cross_convolution_paths(self) -> None:
        with self.assertRaisesRegex(ValueError, "decomposed convolution"):
            convolve_load_green_functions(
                [1.0], [0.1], CombinedFixtureProvider(), direct_attraction_m_s2=0.0
            )
        with self.assertRaisesRegex(ValueError, "combined convolution"):
            convolve_combined_elastic_load_green_functions(
                [1.0], [0.1], AnalyticFixtureProvider(), direct_attraction_m_s2=0.0
            )
        with self.assertRaises(ValueError):
            LoadGreenFunctionMetadata(
                "id", "1", "earth", "source", component_semantics="ambiguous"
            )

    def test_scientific_gate_requires_matching_audit_and_benchmark(self) -> None:
        provider = CombinedFixtureProvider()
        base = {
            "provider_id": "combined-fixture",
            "provider_version": "1",
            "exact_source_commit": "a" * 40,
            "artifact_sha256": "b" * 64,
            "license_id": "GPL-3.0",
            "earth_model": "not-a-physical-earth-model",
            "reference_frame": "CE",
            "normalization": "per_source_mass_kg",
            "component_semantics": "combined_elastic_gravity",
            "angular_distance_unit": "rad",
            "source_equation_audited": True,
            "published_benchmark_id": "unit-test-only",
            "benchmark_passed": True,
        }
        audited_metadata = LoadGreenFunctionMetadata(
            provider_id=provider.metadata.provider_id,
            provider_version=provider.metadata.provider_version,
            earth_model=provider.metadata.earth_model,
            source=provider.metadata.source,
            component_semantics=provider.metadata.component_semantics,
            reference_frame="CE",
        )
        provider.metadata = audited_metadata
        assert_green_function_scientific_use_ready(
            provider, LoadGreenFunctionScientificAudit(**base)
        )

        incomplete = dict(base, benchmark_passed=False)
        with self.assertRaisesRegex(ValueError, "benchmark"):
            assert_green_function_scientific_use_ready(
                provider, LoadGreenFunctionScientificAudit(**incomplete)
            )
        mismatched = dict(base, earth_model="different")
        with self.assertRaisesRegex(ValueError, "earth_model"):
            assert_green_function_scientific_use_ready(
                provider, LoadGreenFunctionScientificAudit(**mismatched)
            )

    def test_scientific_audit_rejects_placeholder_provenance(self) -> None:
        with self.assertRaisesRegex(ValueError, "exact_source_commit"):
            LoadGreenFunctionScientificAudit(
                provider_id="provider",
                provider_version="1",
                exact_source_commit="pending",
                artifact_sha256="b" * 64,
                license_id="GPL-3.0",
                earth_model="PREM",
                reference_frame="CE",
                normalization="per_source_mass_kg",
                component_semantics="combined_elastic_gravity",
                angular_distance_unit="rad",
                source_equation_audited=True,
                published_benchmark_id="benchmark",
                benchmark_passed=True,
            )


if __name__ == "__main__":
    unittest.main()
