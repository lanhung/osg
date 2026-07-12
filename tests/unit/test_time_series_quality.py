"""Missingness, cadence, and no-correction tests for time-series QC."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.signal_processing import assess_time_series_quality


class TestTimeSeriesQuality(unittest.TestCase):
    def test_summary_preserves_indices_across_gaps_and_cadence_breaks(self) -> None:
        summary = assess_time_series_quality(
            [0.0, 1.0, 2.0, 3.0, 5.0, 6.0, 7.0, 8.0],
            [0.0, 1.0, None, 10.0, 11.0, 30.0, math.nan, 31.0],
            1.0,
            discontinuity_threshold=10.0,
        )
        self.assertEqual(summary.timebase.missing_samples, 2)
        self.assertEqual(summary.timebase.cadence_breaks, 1)
        self.assertEqual(summary.discontinuity_later_indices, (5,))
        self.assertEqual(summary.maximum_finite_adjacent_difference, 19.0)
        self.assertEqual(summary.missing_fraction, 0.25)

    def test_flagging_does_not_change_retained_samples(self) -> None:
        samples = [0.0, 1.0, 100.0, 2.0]
        summary = assess_time_series_quality(
            [0.0, 1.0, 2.0, 3.0],
            samples,
            1.0,
            discontinuity_threshold=50.0,
        )
        self.assertEqual(summary.discontinuity_later_indices, (2, 3))
        self.assertEqual(summary.timebase.segments[0].samples, tuple(samples))

    def test_threshold_must_be_explicit_and_positive(self) -> None:
        with self.assertRaises(ValueError):
            assess_time_series_quality([0.0, 1.0], [0.0, 1.0], 1.0, discontinuity_threshold=0.0)


if __name__ == "__main__":
    unittest.main()
