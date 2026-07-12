"""Tests for unit-explicit instrument noise curves."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.instruments import NoiseCurve


def _curve() -> NoiseCurve:
    return NoiseCurve(
        instrument_id="test-gravimeter",
        observable="vertical_gravity",
        asd_unit="m s^-2 Hz^-1/2",
        frequencies_hz=(1.0e-3, 1.0e-2, 1.0e-1),
        asd=(1.0e-7, 1.0e-8, 1.0e-9),
        source="analytic test fixture",
        curve_version="test-v1",
        digitization_relative_uncertainty=0.01,
    )


class TestNoiseCurve(unittest.TestCase):
    def test_nodes_are_returned_exactly(self) -> None:
        curve = _curve()
        for frequency, expected in zip(curve.frequencies_hz, curve.asd, strict=True):
            self.assertEqual(curve.asd_at(frequency), expected)

    def test_log_log_midpoint_follows_power_law(self) -> None:
        curve = _curve()
        frequency = math.sqrt(1.0e-3 * 1.0e-2)
        expected = math.sqrt(1.0e-7 * 1.0e-8)
        self.assertAlmostEqual(curve.asd_at(frequency), expected, delta=expected * 2e-15)

    def test_psd_is_square_of_asd(self) -> None:
        curve = _curve()
        frequency = 0.01
        self.assertEqual(curve.psd_at(frequency), curve.asd_at(frequency) ** 2)

    def test_extrapolation_is_rejected(self) -> None:
        curve = _curve()
        with self.assertRaisesRegex(ValueError, "outside curve range"):
            curve.asd_at(1.0e-4)
        with self.assertRaisesRegex(ValueError, "outside curve range"):
            curve.asd_at(1.0)

    def test_invalid_curve_metadata_and_points_are_rejected(self) -> None:
        common = {
            "instrument_id": "test",
            "observable": "vertical_gravity",
            "asd_unit": "m s^-2 Hz^-1/2",
            "source": "fixture",
            "curve_version": "v1",
        }
        with self.assertRaises(ValueError):
            NoiseCurve(frequencies_hz=(1.0,), asd=(2.0,), **common)
        with self.assertRaises(ValueError):
            NoiseCurve(frequencies_hz=(2.0, 1.0), asd=(1.0, 2.0), **common)
        with self.assertRaises(ValueError):
            NoiseCurve(frequencies_hz=(1.0, 2.0), asd=(1.0, 0.0), **common)
        with self.assertRaises(ValueError):
            NoiseCurve(
                frequencies_hz=(1.0, 2.0),
                asd=(1.0, 2.0),
                digitization_relative_uncertainty=-0.1,
                **common,
            )


if __name__ == "__main__":
    unittest.main()
