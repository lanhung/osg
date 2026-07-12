"""Conversion, provenance, and observable tests for literature noise anchors."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from oceangravity.instruments import load_noise_curves  # noqa: E402


class TestInstrumentManifest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.curves = load_noise_curves(ROOT / "data/manifests/instrument_noise_curves.json")

    def test_expected_instruments_and_observable_groups(self) -> None:
        self.assertEqual(len(self.curves), 5)
        gravity = {
            key for key, curve in self.curves.items() if curve.observable == "vertical_gravity"
        }
        gradient = {
            key for key, curve in self.curves.items() if curve.observable == "gravity_gradient"
        }
        self.assertEqual(len(gravity), 3)
        self.assertEqual(len(gradient), 2)
        self.assertTrue(gravity.isdisjoint(gradient))

    def test_igrav_db_to_asd_conversion(self) -> None:
        curve = self.curves["igrav_quiet_j9_self_noise_anchor"]
        expected_psd = 10.0 ** (-180.0 / 10.0)
        self.assertEqual(curve.asd_at(0.01), math.sqrt(expected_psd))
        self.assertEqual(curve.asd_at(0.01), 1.0e-9)

    def test_reported_unit_conversions(self) -> None:
        self.assertEqual(
            self.curves["aqg_a01_field_short_term_anchor"].asd_at(0.01),
            750.0e-9,
        )
        self.assertEqual(
            self.curves["fg5_228_short_term_anchor"].asd_at(0.01),
            450.0e-9,
        )
        self.assertEqual(
            self.curves["mcguirk_atom_gradiometer_anchor"].asd_at(0.01),
            4.0e-9,
        )
        self.assertEqual(
            self.curves["goce_egg_conservative_design_anchor"].asd_at(0.01),
            5.0e-12,
        )

    def test_assumptions_and_operating_conditions_are_not_empty(self) -> None:
        for curve in self.curves.values():
            self.assertTrue(curve.interpretation)
            self.assertTrue(curve.operating_conditions)
            self.assertTrue(curve.model_uncertainty_note)

    def test_no_curve_extrapolates(self) -> None:
        for curve in self.curves.values():
            with self.assertRaises(ValueError):
                curve.asd_at(curve.frequencies_hz[0] / 2.0)
            with self.assertRaises(ValueError):
                curve.asd_at(curve.frequencies_hz[-1] * 2.0)


if __name__ == "__main__":
    unittest.main()
