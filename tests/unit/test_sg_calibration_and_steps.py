"""Paper 2 SG calibration and explicit step-ledger tests."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.signal_processing import (  # noqa: E402
    GravityCalibration,
    InstrumentStepDecision,
    apply_feedback_calibration,
    apply_instrument_step_decisions,
)


def _calibration(**changes):
    values = {
        "calibration_id": "FG5-comparison-v1",
        "factor_m_s2_per_volt": -2.0e-8,
        "factor_standard_uncertainty_m_s2_per_volt": 1.0e-10,
        "voltage_offset_v": 1.0,
        "gravity_offset_m_s2": 3.0e-9,
        "gravity_offset_standard_uncertainty_m_s2": 2.0e-11,
        "valid_start_utc": "2024-01-01T00:00:00Z",
        "valid_end_utc": "2025-01-01T00:00:00Z",
        "source": "unit-test fixture",
    }
    values.update(changes)
    return GravityCalibration(**values)


class TestSgCalibrationAndSteps(unittest.TestCase):
    def test_feedback_calibration_preserves_sign_offset_and_uncertainty(self) -> None:
        times = ("2024-01-01T00:00:00Z", "2024-01-02T00:00:00Z")
        result = apply_feedback_calibration(times, [1.0, 3.0], _calibration())
        self.assertEqual(result.sample_times_utc, times)
        self.assertEqual(result.values_m_s2, (3.0e-9, -3.7e-8))
        self.assertAlmostEqual(result.standard_uncertainty_m_s2[0], 2.0e-11)
        self.assertAlmostEqual(
            result.standard_uncertainty_m_s2[1], math.hypot(2.0e-10, 2.0e-11)
        )
        self.assertEqual(result.calibration_id, "FG5-comparison-v1")

    def test_invalid_calibration_and_voltage_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            _calibration(factor_m_s2_per_volt=0.0)
        with self.assertRaises(ValueError):
            _calibration(valid_end_utc="2023-01-01T00:00:00Z")
        with self.assertRaises(ValueError):
            apply_feedback_calibration([], [], _calibration())

    def test_calibration_validity_and_order_are_enforced(self) -> None:
        calibration = _calibration()
        with self.assertRaisesRegex(ValueError, "validity"):
            apply_feedback_calibration(
                ["2025-01-01T00:00:00Z"], [1.0], calibration
            )
        with self.assertRaisesRegex(ValueError, "strictly increasing"):
            apply_feedback_calibration(
                ["2024-01-02T00:00:00Z", "2024-01-01T00:00:00Z"],
                [1.0, 2.0],
                calibration,
            )
        with self.assertRaisesRegex(ValueError, "equal nonzero length"):
            apply_feedback_calibration(
                ["2024-01-01T00:00:00Z"], [1.0, 2.0], calibration
            )

    def test_multiple_declared_steps_are_removed_persistently(self) -> None:
        decisions = (
            InstrumentStepDecision("late", 4, -2.0, "log", "maintenance"),
            InstrumentStepDecision("early", 2, 5.0, "log", "instrument reset"),
        )
        result = apply_instrument_step_decisions(
            [1.0, 2.0, 8.0, 9.0, 8.0, 9.0], decisions
        )
        self.assertEqual(result.removed_cumulative_step_m_s2, (0.0, 0.0, 5.0, 5.0, 3.0, 3.0))
        self.assertEqual(result.corrected_m_s2, (1.0, 2.0, 3.0, 4.0, 5.0, 6.0))
        self.assertEqual(result.applied_decision_ids, ("early", "late"))

    def test_ambiguous_or_out_of_range_step_decisions_are_rejected(self) -> None:
        one = InstrumentStepDecision("one", 1, 2.0, "log", "fixture")
        two = InstrumentStepDecision("two", 1, 3.0, "log", "fixture")
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            apply_instrument_step_decisions([1.0, 2.0], (one, two))
        invalid = InstrumentStepDecision("bad", 0, 1.0, "log", "fixture")
        with self.assertRaises(ValueError):
            apply_instrument_step_decisions([1.0, 2.0], (invalid,))


if __name__ == "__main__":
    unittest.main()
