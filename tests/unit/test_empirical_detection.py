"""Finite-record and tie-safety tests for operational false-alarm thresholds."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.evaluation import (  # noqa: E402
    QuietScoreWindow,
    audit_quiet_window_false_positives,
    calibrate_empirical_threshold,
    empirical_detection_probability,
)


class TestEmpiricalDetection(unittest.TestCase):
    def test_short_record_forces_zero_exceedance_threshold(self) -> None:
        calibration = calibrate_empirical_threshold(
            [0.1, 0.2, 0.3, 0.4],
            window_step_s=60.0,
            target_false_alarms_per_30_days=1.0,
        )
        self.assertEqual(calibration.observed_exceedances, 0)
        self.assertGreater(calibration.threshold, 0.4)
        self.assertEqual(calibration.observed_false_alarms_per_30_days, 0.0)
        self.assertGreater(
            calibration.minimum_nonzero_resolvable_false_alarms_per_30_days,
            1.0,
        )

    def test_longer_record_selects_lowest_threshold_under_target(self) -> None:
        # One score per hour and 3000 hours: one exceedance maps to 0.24/month.
        scores = [float(value) for value in range(3000)]
        calibration = calibrate_empirical_threshold(
            scores,
            window_step_s=3600.0,
            target_false_alarms_per_30_days=0.5,
        )
        self.assertEqual(calibration.observed_exceedances, 2)
        self.assertEqual(calibration.threshold, 2998.0)
        self.assertAlmostEqual(calibration.observed_false_alarms_per_30_days, 0.48)

    def test_tied_extremes_are_handled_conservatively(self) -> None:
        scores = [0.0] * 100 + [10.0, 10.0]
        calibration = calibrate_empirical_threshold(
            scores,
            window_step_s=86_400.0,
            target_false_alarms_per_30_days=0.3,
        )
        self.assertEqual(calibration.observed_exceedances, 0)
        self.assertGreater(calibration.threshold, 10.0)

    def test_detection_probability_uses_frozen_threshold(self) -> None:
        self.assertEqual(empirical_detection_probability([1.0, 2.0, 3.0, 4.0], 2.5), 0.5)
        with self.assertRaises(ValueError):
            empirical_detection_probability([math.nan], 1.0)

    def test_quiet_threshold_is_frozen_before_heldout_evaluation(self) -> None:
        windows = (
            QuietScoreWindow("Q-cal-1", "threshold_calibration", (0.0, 1.0), 86_400.0),
            QuietScoreWindow("Q-cal-2", "threshold_calibration", (0.5, 1.5), 86_400.0),
            QuietScoreWindow("Q-test-1", "held_out", (1.0, 2.0), 86_400.0),
            QuietScoreWindow("Q-test-2", "held_out", (0.0, 3.0), 86_400.0),
        )
        audit = audit_quiet_window_false_positives(
            windows, target_false_alarms_per_30_days=1.0
        )
        self.assertGreater(audit.threshold.threshold, 1.5)
        self.assertEqual(audit.heldout_exceedance_count, 2)
        self.assertEqual(
            audit.heldout_triggered_window_ids, ("Q-test-1", "Q-test-2")
        )
        self.assertEqual(audit.heldout_false_alarms_per_30_days, 15.0)
        self.assertFalse(audit.passes_target_rate)

    def test_quiet_audit_requires_both_splits_and_common_step(self) -> None:
        calibration = QuietScoreWindow(
            "Q-cal", "threshold_calibration", (0.0, 1.0), 3600.0
        )
        heldout = QuietScoreWindow("Q-test", "held_out", (0.0, 1.0), 60.0)
        with self.assertRaisesRegex(ValueError, "same decision step"):
            audit_quiet_window_false_positives(
                (calibration, heldout), target_false_alarms_per_30_days=1.0
            )
        with self.assertRaisesRegex(ValueError, "calibration and held-out"):
            audit_quiet_window_false_positives(
                (calibration,), target_false_alarms_per_30_days=1.0
            )


if __name__ == "__main__":
    unittest.main()
