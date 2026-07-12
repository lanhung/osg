"""Held-out time-dependent detection and persistence tests."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.evaluation import (
    earliest_reliable_detection_time,
    time_dependent_detection_probability,
)


class TestTimeDependentDetection(unittest.TestCase):
    def test_detection_probability_is_computed_per_time_on_held_out_rows(self) -> None:
        points = time_dependent_detection_probability(
            [60.0, 120.0, 180.0, 240.0],
            [
                [0.0, 2.0, 3.0, 4.0],
                [0.0, 0.5, 2.5, 3.0],
                [0.0, 2.5, 1.0, 3.0],
                [0.0, 3.0, 3.5, 4.0],
            ],
            threshold=2.0,
        )
        self.assertEqual(
            [point.detection_probability for point in points],
            [0.0, 0.75, 0.75, 1.0],
        )
        self.assertEqual(points[1].detected_events, 3)

    def test_reliability_can_require_sustained_crossing(self) -> None:
        points = time_dependent_detection_probability(
            [60.0, 120.0, 180.0, 240.0],
            [[3.0, 0.0, 3.0, 3.0], [3.0, 0.0, 3.0, 3.0]],
            threshold=2.0,
        )
        self.assertEqual(earliest_reliable_detection_time(points, 0.9), 60.0)
        self.assertEqual(
            earliest_reliable_detection_time(points, 0.9, required_consecutive_points=2),
            180.0,
        )

    def test_no_reliable_crossing_returns_none(self) -> None:
        points = time_dependent_detection_probability(
            [60.0, 120.0], [[0.0, 1.0], [0.0, 3.0]], threshold=2.0
        )
        self.assertIsNone(earliest_reliable_detection_time(points, 0.9))

    def test_shapes_times_threshold_and_persistence_are_validated(self) -> None:
        with self.assertRaises(ValueError):
            time_dependent_detection_probability([1.0, 1.0], [[0.0, 1.0]], 0.0)
        with self.assertRaises(ValueError):
            time_dependent_detection_probability([1.0, 2.0], [[0.0]], 0.0)
        points = time_dependent_detection_probability([1.0], [[1.0]], 0.0)
        with self.assertRaises(ValueError):
            earliest_reliable_detection_time(points, 0.9, required_consecutive_points=0)


if __name__ == "__main__":
    unittest.main()
