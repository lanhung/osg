"""Time-dependent magnitude reliability tests."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.evaluation import (  # noqa: E402
    earliest_reliable_magnitude_time,
    time_dependent_magnitude_performance,
)


class TestMagnitudePerformance(unittest.TestCase):
    def _points(self):
        return time_dependent_magnitude_performance(
            [120.0, 300.0, 600.0],
            [8.0, 8.1, 8.3, 8.8],
            [
                [7.5, 8.0, 8.0],
                [7.7, 8.0, 8.1],
                [7.8, 8.3, 8.3],
                [8.0, 8.7, 8.8],
            ],
            high_risk_magnitude=8.2,
            lower_intervals=[
                [7.0, 7.8, 7.9],
                [7.0, 7.8, 8.0],
                [7.0, 8.1, 8.2],
                [7.0, 8.5, 8.7],
            ],
            upper_intervals=[
                [8.1, 8.2, 8.2],
                [8.1, 8.2, 8.2],
                [8.1, 8.5, 8.4],
                [8.1, 8.9, 8.9],
            ],
        )

    def test_metrics_separate_regression_risk_and_coverage(self) -> None:
        points = self._points()
        self.assertEqual(points[0].high_risk_sensitivity, 0.0)
        self.assertEqual(points[1].high_risk_sensitivity, 1.0)
        self.assertEqual(points[1].low_risk_specificity, 1.0)
        self.assertEqual(points[1].interval_coverage_probability, 1.0)
        self.assertLess(points[2].mean_absolute_error, points[0].mean_absolute_error)

    def test_reliable_time_requires_all_criteria_and_persistence(self) -> None:
        points = self._points()
        self.assertEqual(
            earliest_reliable_magnitude_time(
                points,
                maximum_mae=0.2,
                minimum_high_risk_sensitivity=0.9,
                minimum_low_risk_specificity=0.9,
                minimum_interval_coverage=0.9,
                required_consecutive_points=2,
            ),
            300.0,
        )

    def test_missing_positive_or_negative_class_cannot_claim_reliability(self) -> None:
        points = time_dependent_magnitude_performance(
            [100.0], [8.5, 8.7], [[8.5], [8.7]], high_risk_magnitude=8.2
        )
        self.assertIsNone(points[0].low_risk_specificity)
        self.assertIsNone(
            earliest_reliable_magnitude_time(
                points,
                maximum_mae=0.1,
                minimum_high_risk_sensitivity=0.9,
                minimum_low_risk_specificity=0.9,
            )
        )


if __name__ == "__main__":
    unittest.main()
