"""Closure and double-count tests for Paper 2 gravity residual assembly."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.loading import (
    GravityCorrectionComponent,
    apply_gravity_correction_chain,
    compute_gravity_residual,
    summarize_gravity_correction_waterfall,
)


def _component(
    identifier: str,
    values,
    effects,
    *,
    preapplied: bool = False,
    uncertainty=None,
    uncertainty_group=None,
):
    return GravityCorrectionComponent(
        component_id=identifier,
        values_m_s2=tuple(values),
        physical_effect_ids=tuple(effects),
        source="unit-test fixture",
        preapplied_to_input=preapplied,
        standard_uncertainty_m_s2=(None if uncertainty is None else tuple(uncertainty)),
        uncertainty_group_id=uncertainty_group,
    )


class TestGravityBudget(unittest.TestCase):
    def test_residual_closes_with_separate_physical_components(self) -> None:
        observed = [10.0, 20.0, 30.0]
        components = [
            _component("solid_tide", [1.0, 2.0, 3.0], ["solid_earth_tide"]),
            _component("atmosphere", [2.0, 3.0, 4.0], ["atmosphere_direct"]),
            _component(
                "ocean",
                [3.0, 4.0, 5.0],
                ["ocean_direct", "ocean_elastic", "ocean_inverse_barometer"],
            ),
        ]
        result = compute_gravity_residual(observed, components)
        self.assertEqual(result.residual_m_s2, (4.0, 11.0, 18.0))
        self.assertLessEqual(result.closure_max_abs_m_s2, 4e-15)
        self.assertEqual(result.uncertainty_status, "incomplete")
        self.assertIsNone(result.residual_standard_uncertainty_m_s2)

    def test_overlapping_inverse_barometer_effect_is_rejected(self) -> None:
        cmems = _component(
            "cmems_ocean",
            [1.0, 1.0],
            ["ocean_direct", "ocean_inverse_barometer"],
        )
        separate_ib = _component(
            "era5_driven_ib",
            [0.5, 0.5],
            ["ocean_inverse_barometer"],
        )
        with self.assertRaisesRegex(ValueError, "ocean_inverse_barometer"):
            compute_gravity_residual([5.0, 5.0], [cmems, separate_ib])

    def test_preapplied_and_length_mismatch_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "already applied"):
            compute_gravity_residual(
                [1.0, 2.0],
                [_component("ntol", [0.1, 0.2], ["ocean_direct"], preapplied=True)],
            )
        with self.assertRaises(ValueError):
            compute_gravity_residual([1.0, 2.0], [_component("short", [0.1], ["hydrology"])])

    def test_ordered_chain_retains_every_intermediate_series(self) -> None:
        observed = [10.0, 20.0]
        first = _component("tide", [1.0, 2.0], ["solid_earth_tide"])
        second = _component("atmosphere", [3.0, 4.0], ["atmosphere_direct"])
        chain = apply_gravity_correction_chain(observed, [first, second])
        self.assertEqual(len(chain.stages), 2)
        self.assertEqual(chain.stages[0].input_m_s2, (10.0, 20.0))
        self.assertEqual(chain.stages[0].output_m_s2, (9.0, 18.0))
        self.assertEqual(chain.stages[1].input_m_s2, (9.0, 18.0))
        self.assertEqual(chain.stages[1].output_m_s2, (6.0, 14.0))
        self.assertEqual(chain.final_residual.residual_m_s2, (6.0, 14.0))
        self.assertEqual(chain.stages[1].peak_absolute_removed_m_s2, 4.0)
        self.assertEqual(chain.stages[1].physical_effect_ids, ("atmosphere_direct",))
        self.assertEqual(chain.stages[1].source, "unit-test fixture")
        self.assertIsNone(chain.stages[1].removed_standard_uncertainty_m_s2)

    def test_waterfall_reports_each_stage_without_altering_series(self) -> None:
        observed = (5.0, -5.0)
        tide = _component("tide", (1.0, -1.0), ("solid_earth_tide",))
        atmosphere = _component("atmosphere", (2.0, -2.0), ("atmosphere_direct",))
        chain = apply_gravity_correction_chain(observed, (tide, atmosphere))
        metrics = summarize_gravity_correction_waterfall(chain)
        self.assertEqual(metrics.initial_rms_m_s2, 5.0)
        self.assertEqual(metrics.final_rms_m_s2, 2.0)
        self.assertAlmostEqual(metrics.total_rms_change_fraction, 0.6)
        self.assertEqual(len(metrics.stages), 2)
        self.assertEqual(metrics.stages[0].removed_rms_m_s2, 1.0)
        self.assertEqual(metrics.stages[0].output_rms_m_s2, 4.0)
        self.assertAlmostEqual(metrics.stages[0].stage_rms_change_fraction, 0.2)
        self.assertEqual(chain.final_residual.residual_m_s2, (2.0, -2.0))
        self.assertEqual(metrics.uncertainty_status, "incomplete")

    def test_uncertainty_groups_preserve_declared_correlation(self) -> None:
        observed = [10.0, 20.0]
        independent = _component(
            "independent",
            [1.0, 1.0],
            ["effect_a"],
            uncertainty=[2.0, 2.0],
            uncertainty_group="model_a",
        )
        shared_one = _component(
            "shared_one",
            [1.0, 1.0],
            ["effect_b"],
            uncertainty=[3.0, 3.0],
            uncertainty_group="shared_model",
        )
        shared_two = _component(
            "shared_two",
            [1.0, 1.0],
            ["effect_c"],
            uncertainty=[4.0, 4.0],
            uncertainty_group="shared_model",
        )
        result = compute_gravity_residual(
            observed,
            (independent, shared_one, shared_two),
            observed_standard_uncertainty_m_s2=(1.0, 1.0),
            require_complete_uncertainty=True,
        )
        self.assertEqual(result.uncertainty_status, "complete")
        self.assertEqual(result.uncertainty_group_ids, ("model_a", "shared_model"))
        expected = (1.0**2 + 2.0**2 + (3.0 + 4.0) ** 2) ** 0.5
        self.assertAlmostEqual(result.residual_standard_uncertainty_m_s2[0], expected)

    def test_incomplete_uncertainty_cannot_silently_pass_strict_gate(self) -> None:
        component = _component("known", [1.0], ["effect"])
        with self.assertRaisesRegex(ValueError, "incomplete"):
            compute_gravity_residual(
                [2.0],
                (component,),
                observed_standard_uncertainty_m_s2=(0.1,),
                require_complete_uncertainty=True,
            )
        with self.assertRaisesRegex(ValueError, "supplied together"):
            _component("bad", [1.0], ["effect"], uncertainty=[0.1])

    def test_zero_rms_has_explicit_undefined_fraction(self) -> None:
        zero = _component("zero", (0.0, 0.0), ("fixture",))
        chain = apply_gravity_correction_chain((0.0, 0.0), (zero,))
        metrics = summarize_gravity_correction_waterfall(chain)
        self.assertIsNone(metrics.total_rms_change_fraction)
        self.assertIsNone(metrics.stages[0].stage_rms_change_fraction)


if __name__ == "__main__":
    unittest.main()
