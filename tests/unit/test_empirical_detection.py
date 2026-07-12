"""Finite-record and tie-safety tests for operational false-alarm thresholds."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.evaluation import (  # noqa: E402
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


if __name__ == "__main__":
    unittest.main()
