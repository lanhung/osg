"""Causal precipitation-response and gravity-ledger integration tests."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.constants import GRAVITATIONAL_CONSTANT  # noqa: E402
from oceangravity.loading import (  # noqa: E402
    double_exponential_precipitation_storage,
    hydrology_bouguer_correction_component,
)


class TestHydrologyResponse(unittest.TestCase):
    def test_impulse_response_is_causal_and_uses_explicit_weights(self) -> None:
        result = double_exponential_precipitation_storage(
            (0.0, 10.0, 30.0),
            (0.1, 0.0, 0.0),
            fast_time_constant_s=10.0,
            slow_time_constant_s=100.0,
            fast_fraction=0.25,
        )
        self.assertEqual(result.effective_water_height_m[0], 0.1)
        expected_second = 0.25 * 0.1 * math.exp(-1.0) + 0.75 * 0.1 * math.exp(-0.1)
        expected_third = 0.25 * 0.1 * math.exp(-3.0) + 0.75 * 0.1 * math.exp(-0.3)
        self.assertAlmostEqual(result.effective_water_height_m[1], expected_second)
        self.assertAlmostEqual(result.effective_water_height_m[2], expected_third)
        self.assertEqual(result.total_precipitation_m, 0.1)

    def test_each_new_increment_enters_after_elapsed_decay(self) -> None:
        result = double_exponential_precipitation_storage(
            (0.0, 5.0),
            (0.2, 0.3),
            fast_time_constant_s=5.0,
            slow_time_constant_s=10.0,
            fast_fraction=1.0,
        )
        self.assertAlmostEqual(result.fast_storage_m[1], 0.2 * math.exp(-1.0) + 0.3)
        self.assertEqual(result.effective_water_height_m, result.fast_storage_m)

    def test_component_preserves_sign_effect_id_and_uncertainty(self) -> None:
        component = hydrology_bouguer_correction_component(
            (0.01, 0.02),
            component_id="era5_rainfall_local_slab",
            source="physics fixture",
            equivalent_height_standard_uncertainty_m=(0.001, 0.002),
            uncertainty_group_id="hydrology_model",
        )
        factor = 2.0 * math.pi * GRAVITATIONAL_CONSTANT.value * 1_000.0
        self.assertEqual(component.physical_effect_ids, ("land_hydrology_direct_local_slab",))
        self.assertAlmostEqual(component.values_m_s2[0], -factor * 0.01)
        self.assertAlmostEqual(component.standard_uncertainty_m_s2[1], factor * 0.002)
        self.assertEqual(component.uncertainty_group_id, "hydrology_model")

    def test_invalid_inputs_and_incomplete_uncertainty_declaration_fail(self) -> None:
        with self.assertRaisesRegex(ValueError, "nonnegative"):
            double_exponential_precipitation_storage(
                (0.0,),
                (-0.1,),
                fast_time_constant_s=1.0,
                slow_time_constant_s=2.0,
                fast_fraction=0.5,
            )
        with self.assertRaisesRegex(ValueError, "fast < slow"):
            double_exponential_precipitation_storage(
                (0.0,),
                (0.1,),
                fast_time_constant_s=2.0,
                slow_time_constant_s=2.0,
                fast_fraction=0.5,
            )
        with self.assertRaisesRegex(ValueError, "supplied together"):
            hydrology_bouguer_correction_component(
                (0.01,),
                component_id="hydrology",
                source="fixture",
                equivalent_height_standard_uncertainty_m=(0.001,),
            )


if __name__ == "__main__":
    unittest.main()
