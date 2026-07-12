"""Tests for explicit Gaussian reference detection thresholds."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.evaluation import (
    gaussian_detection_probability,
    gaussian_threshold_for_false_alarm,
    required_snr_for_detection_probability,
)


class TestGaussianDetectionReference(unittest.TestCase):
    def test_known_one_sided_thresholds(self) -> None:
        self.assertAlmostEqual(gaussian_threshold_for_false_alarm(0.05), 1.6448536269514722)
        self.assertAlmostEqual(gaussian_threshold_for_false_alarm(0.001), 3.090232306167813)

    def test_trials_correction_recovers_family_probability(self) -> None:
        single = gaussian_threshold_for_false_alarm(0.01, independent_trials=1)
        many = gaussian_threshold_for_false_alarm(0.01, independent_trials=1_000)
        self.assertGreater(many, single)

    def test_required_snr_inverts_detection_probability(self) -> None:
        threshold = gaussian_threshold_for_false_alarm(0.001)
        required = required_snr_for_detection_probability(threshold, 0.9)
        self.assertAlmostEqual(gaussian_detection_probability(required, threshold), 0.9)
        self.assertAlmostEqual(required, 4.371783871712414)

    def test_threshold_snr_gives_fifty_percent_detection(self) -> None:
        self.assertEqual(gaussian_detection_probability(5.0, 5.0), 0.5)

    def test_invalid_probabilities_trials_and_snr_are_rejected(self) -> None:
        for probability in (0.0, 1.0):
            with self.assertRaises(ValueError):
                gaussian_threshold_for_false_alarm(probability)
        with self.assertRaises(ValueError):
            gaussian_threshold_for_false_alarm(0.1, independent_trials=True)
        with self.assertRaises(ValueError):
            gaussian_detection_probability(-1.0, 2.0)
        with self.assertRaises(ValueError):
            required_snr_for_detection_probability(2.0, 1.0)


if __name__ == "__main__":
    unittest.main()
