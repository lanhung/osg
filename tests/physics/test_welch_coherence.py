"""Welch coherence normalization, phase cancellation, and mask tests."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.signal_processing import (
    welch_magnitude_squared_coherence,
)


def _sinusoid(length: int, cycles: int) -> tuple[float, ...]:
    return tuple(math.sin(2.0 * math.pi * cycles * index / length) for index in range(length))


class TestWelchCoherence(unittest.TestCase):
    def test_identical_repeated_signal_has_unit_coherence_at_signal_bin(self) -> None:
        segment = _sinusoid(16, 2)
        series = segment * 3
        result = welch_magnitude_squared_coherence(
            series,
            series,
            1.0,
            segment_length_samples=16,
            overlap_samples=0,
        )
        self.assertEqual(result.used_segment_starts, (0, 16, 32))
        self.assertAlmostEqual(result.magnitude_squared_coherence[2], 1.0)

    def test_cross_phase_cancellation_is_not_misreported_as_coherence(self) -> None:
        segment = _sinusoid(16, 2)
        first = segment * 2
        second = segment + tuple(-value for value in segment)
        result = welch_magnitude_squared_coherence(
            first,
            second,
            1.0,
            segment_length_samples=16,
            overlap_samples=0,
        )
        self.assertLess(result.magnitude_squared_coherence[2], 1e-28)

    def test_mask_discards_whole_segments_and_requires_two(self) -> None:
        segment = _sinusoid(8, 1)
        series = segment * 3
        mask = [True] * len(series)
        mask[9] = False
        result = welch_magnitude_squared_coherence(
            series,
            series,
            1.0,
            segment_length_samples=8,
            overlap_samples=0,
            inclusion_mask=mask,
        )
        self.assertEqual(result.used_segment_starts, (0, 16))
        self.assertEqual(result.discarded_segment_starts, (8,))
        mask[16] = False
        with self.assertRaisesRegex(ValueError, "at least two"):
            welch_magnitude_squared_coherence(
                series,
                series,
                1.0,
                segment_length_samples=8,
                overlap_samples=0,
                inclusion_mask=mask,
            )

    def test_invalid_overlap_and_short_record_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            welch_magnitude_squared_coherence(
                (1.0, 2.0, 3.0, 4.0),
                (1.0, 2.0, 3.0, 4.0),
                1.0,
                segment_length_samples=4,
                overlap_samples=4,
            )
        with self.assertRaises(ValueError):
            welch_magnitude_squared_coherence(
                (1.0, 2.0, 3.0),
                (1.0, 2.0, 3.0),
                1.0,
                segment_length_samples=4,
                overlap_samples=0,
            )


if __name__ == "__main__":
    unittest.main()
