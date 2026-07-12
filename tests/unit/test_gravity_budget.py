"""Closure and double-count tests for Paper 2 gravity residual assembly."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.loading import (  # noqa: E402
    GravityCorrectionComponent,
    compute_gravity_residual,
)


def _component(identifier: str, values, effects, *, preapplied: bool = False):
    return GravityCorrectionComponent(
        component_id=identifier,
        values_m_s2=tuple(values),
        physical_effect_ids=tuple(effects),
        source="unit-test fixture",
        preapplied_to_input=preapplied,
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
            compute_gravity_residual(
                [1.0, 2.0], [_component("short", [0.1], ["hydrology"])]
            )


if __name__ == "__main__":
    unittest.main()
