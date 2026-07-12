"""Cadence, gap, and no-synthesis tests for time-series segmentation."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.signal_processing import split_uniform_time_series  # noqa: E402


class TestTimebaseSegmentation(unittest.TestCase):
    def test_missing_and_cadence_breaks_are_split_without_synthesis(self) -> None:
        result = split_uniform_time_series(
            [0.0, 1.0, 2.0, 3.0, 5.0, 6.0, 7.0, 8.0],
            [10.0, 11.0, None, 13.0, 15.0, 16.0, math.nan, 18.0],
            1.0,
        )
        self.assertEqual(result.missing_samples, 2)
        self.assertEqual(result.cadence_breaks, 1)
        self.assertEqual(result.dropped_short_run_samples, 2)
        self.assertEqual(result.retained_samples, 4)
        self.assertEqual(len(result.segments), 2)
        self.assertEqual(result.segments[0].samples, (10.0, 11.0))
        self.assertEqual(result.segments[1].samples, (15.0, 16.0))
        self.assertEqual(
            result.retained_samples + result.missing_samples + result.dropped_short_run_samples,
            result.input_samples,
        )

    def test_relative_tolerance_is_explicit(self) -> None:
        accepted = split_uniform_time_series(
            [0.0, 1.0000005, 2.0000002], [1.0, 2.0, 3.0], 1.0
        )
        self.assertEqual(len(accepted.segments), 1)
        strict = split_uniform_time_series(
            [0.0, 1.0000005, 2.0000002],
            [1.0, 2.0, 3.0],
            1.0,
            relative_interval_tolerance=1e-8,
        )
        self.assertEqual(strict.cadence_breaks, 2)
        self.assertEqual(strict.retained_samples, 0)
        self.assertEqual(strict.dropped_short_run_samples, 3)

    def test_timestamps_and_configuration_are_validated(self) -> None:
        with self.assertRaises(ValueError):
            split_uniform_time_series([0.0, 0.0], [1.0, 2.0], 1.0)
        with self.assertRaises(ValueError):
            split_uniform_time_series([0.0, math.nan], [1.0, 2.0], 1.0)
        with self.assertRaises(ValueError):
            split_uniform_time_series([0.0, 1.0], [1.0, 2.0], 0.0)
        with self.assertRaises(ValueError):
            split_uniform_time_series(
                [0.0, 1.0], [1.0, 2.0], 1.0, minimum_segment_samples=True
            )


if __name__ == "__main__":
    unittest.main()
