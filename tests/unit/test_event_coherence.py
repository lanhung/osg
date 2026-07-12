"""Masked Welch coherence tests for Paper 2 event comparisons."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.signal_processing import (  # noqa: E402
    mean_coherence_in_band,
    welch_magnitude_squared_coherence,
)


class TestEventCoherence(unittest.TestCase):
    def test_identical_signal_has_unit_coherence_where_power_exists(self) -> None:
        samples = tuple(
            math.sin(2.0 * math.pi * index / 8.0)
            + 0.3 * math.sin(2.0 * math.pi * index / 4.0)
            for index in range(32)
        )
        result = welch_magnitude_squared_coherence(
            samples,
            samples,
            1.0,
            segment_length_samples=8,
            overlap_samples=0,
        )
        defined = [value for value in result.magnitude_squared_coherence if value is not None]
        self.assertTrue(defined)
        self.assertTrue(all(abs(value - 1.0) < 1e-12 for value in defined))
        self.assertEqual(result.used_segment_starts, (0, 8, 16, 24))

    def test_mask_rejects_whole_windows_without_sample_concatenation(self) -> None:
        observed = tuple(float(index % 5) for index in range(24))
        modeled = tuple(0.5 * value for value in observed)
        mask = [True] * 24
        mask[9] = False
        result = welch_magnitude_squared_coherence(
            observed,
            modeled,
            1.0,
            segment_length_samples=8,
            overlap_samples=0,
            inclusion_mask=mask,
        )
        self.assertEqual(result.used_segment_starts, (0, 16))
        self.assertEqual(result.discarded_segment_starts, (8,))

    def test_single_segment_and_undefined_band_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least two"):
            welch_magnitude_squared_coherence(
                range(8), range(8), 1.0, segment_length_samples=8, overlap_samples=0
            )
        result = welch_magnitude_squared_coherence(
            tuple(range(16)),
            tuple(range(16)),
            1.0,
            segment_length_samples=8,
            overlap_samples=0,
        )
        self.assertGreater(mean_coherence_in_band(result, 0.01, 0.49), 0.99)
        with self.assertRaisesRegex(ValueError, "no defined"):
            mean_coherence_in_band(result, 2.0, 3.0)


if __name__ == "__main__":
    unittest.main()
