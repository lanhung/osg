"""Coverage-first classification tests for instrument noise curves."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.evaluation import (
    evaluate_gradient_signal_against_curve,
    evaluate_gravity_signal_against_curve,
)
from oceangravity.instruments import NoiseCurve


def _curve(minimum: float, maximum: float, asd: float = 1.0) -> NoiseCurve:
    return NoiseCurve(
        instrument_id=f"curve-{minimum}-{maximum}",
        observable="vertical_gravity",
        asd_unit="m s^-2 Hz^-1/2",
        frequencies_hz=(minimum, maximum),
        asd=(asd, asd),
        source="test fixture",
        curve_version="1",
    )


class TestCurveDetectability(unittest.TestCase):
    def test_in_band_sine_has_full_coverage_and_expected_classification(self) -> None:
        count = 256
        interval = 1.0
        frequency_bin = 20
        frequency = frequency_bin / (count * interval)
        samples = tuple(
            math.sin(2.0 * math.pi * frequency_bin * index / count) for index in range(count)
        )
        result = evaluate_gravity_signal_against_curve(
            samples,
            interval,
            _curve(0.01, 0.49, asd=1.0),
            required_expected_snr=1.0,
        )
        self.assertEqual(result.status, "detectable_under_curve_model")
        self.assertAlmostEqual(result.signal_energy_coverage_fraction, 1.0)
        self.assertAlmostEqual(
            result.matched_filter_snr_in_covered_band,
            math.sqrt(count),
            delta=math.sqrt(count) * 2e-14,
        )
        self.assertAlmostEqual(frequency, 0.078125)

    def test_no_overlap_returns_unknown_without_snr(self) -> None:
        samples = tuple(math.sin(2.0 * math.pi * 5 * index / 64) for index in range(64))
        result = evaluate_gravity_signal_against_curve(
            samples,
            1.0,
            _curve(1.0, 2.0),
            required_expected_snr=1.0,
        )
        self.assertEqual(result.status, "no_frequency_coverage")
        self.assertIsNone(result.matched_filter_snr_in_covered_band)

    def test_partial_energy_is_not_classified_even_when_local_snr_is_large(self) -> None:
        count = 256
        samples = tuple(
            math.sin(2.0 * math.pi * 10 * index / count)
            + math.sin(2.0 * math.pi * 60 * index / count)
            for index in range(count)
        )
        result = evaluate_gravity_signal_against_curve(
            samples,
            1.0,
            _curve(0.02, 0.1, asd=1.0e-9),
            required_expected_snr=1.0,
            minimum_signal_energy_coverage=0.9,
        )
        self.assertEqual(result.status, "partial_band_not_classified")
        self.assertAlmostEqual(result.signal_energy_coverage_fraction, 0.5, delta=1e-14)
        self.assertGreater(result.matched_filter_snr_in_covered_band, 1.0)

    def test_predeclared_numerical_coverage_floor_zeros_spectral_leakage(self) -> None:
        count = 256
        samples = tuple(
            math.sin(2.0 * math.pi * 60 * index / count)
            + 1.0e-15 * math.sin(2.0 * math.pi * 10 * index / count)
            for index in range(count)
        )
        result = evaluate_gravity_signal_against_curve(
            samples,
            1.0,
            _curve(0.03, 0.05, asd=1.0),
            required_expected_snr=1.0,
            minimum_signal_energy_coverage=0.9,
            numerical_energy_coverage_floor=1.0e-24,
        )
        self.assertEqual(result.status, "partial_band_not_classified")
        self.assertEqual(result.signal_energy_coverage_fraction, 0.0)
        self.assertEqual(result.matched_filter_snr_in_covered_band, 0.0)

    def test_zero_signal_and_observable_mismatch(self) -> None:
        result = evaluate_gravity_signal_against_curve(
            [0.0] * 64,
            1.0,
            _curve(0.01, 0.4),
            required_expected_snr=1.0,
        )
        self.assertEqual(result.status, "zero_signal")
        gradient_curve = NoiseCurve(
            instrument_id="gradient",
            observable="gravity_gradient",
            asd_unit="s^-2 Hz^-1/2",
            frequencies_hz=(0.01, 0.4),
            asd=(1.0, 1.0),
            source="fixture",
            curve_version="1",
        )
        with self.assertRaises(ValueError):
            evaluate_gravity_signal_against_curve(
                [0.0] * 64,
                1.0,
                gradient_curve,
                required_expected_snr=1.0,
            )

    def test_invalid_threshold_and_coverage_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_gravity_signal_against_curve(
                [0.0] * 64,
                1.0,
                _curve(0.01, 0.4),
                required_expected_snr=-1.0,
            )
        with self.assertRaises(ValueError):
            evaluate_gravity_signal_against_curve(
                [0.0] * 64,
                1.0,
                _curve(0.01, 0.4),
                required_expected_snr=1.0,
                minimum_signal_energy_coverage=0.0,
            )
        with self.assertRaises(ValueError):
            evaluate_gravity_signal_against_curve(
                [0.0] * 64,
                1.0,
                _curve(0.01, 0.4),
                required_expected_snr=1.0,
                minimum_signal_energy_coverage=0.9,
                numerical_energy_coverage_floor=0.9,
            )

    def test_gradient_wrapper_uses_gradient_observable_and_units(self) -> None:
        count = 128
        samples = tuple(
            1e-9 * math.sin(2.0 * math.pi * 8 * index / count) for index in range(count)
        )
        curve = NoiseCurve(
            instrument_id="gradient",
            observable="gravity_gradient",
            asd_unit="s^-2 Hz^-1/2",
            frequencies_hz=(0.01, 0.4),
            asd=(1e-10, 1e-10),
            source="fixture",
            curve_version="1",
        )
        result = evaluate_gradient_signal_against_curve(
            samples,
            1.0,
            curve,
            required_expected_snr=1.0,
        )
        self.assertEqual(result.status, "detectable_under_curve_model")
        with self.assertRaises(ValueError):
            evaluate_gravity_signal_against_curve(
                samples,
                1.0,
                curve,
                required_expected_snr=1.0,
            )


if __name__ == "__main__":
    unittest.main()
