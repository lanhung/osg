"""Non-overlapping masked event matched-filter SNR tests."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.signal_processing import (
    masked_event_matched_filter_snr,
    matched_filter_snr,
    one_sided_spectrum,
)


class TestMaskedEventSnr(unittest.TestCase):
    def test_two_equal_segments_combine_in_quadrature(self) -> None:
        segment = tuple(2.0 * math.sin(2.0 * math.pi * 2 * index / 16) for index in range(16))
        reference = one_sided_spectrum(segment, 1.0)
        noise = (3.0,) * len(reference.frequencies_hz)
        single = matched_filter_snr(reference.frequencies_hz, reference.fourier_amplitude, noise)
        result = masked_event_matched_filter_snr(
            segment * 2,
            1.0,
            noise,
            segment_length_samples=16,
        )
        self.assertAlmostEqual(result.matched_filter_snr, math.sqrt(2.0) * single)
        self.assertEqual(result.segment_snrs, (single, single))
        self.assertEqual(result.used_segment_starts, (0, 16))

    def test_mask_discards_whole_segment_and_trailing_samples_are_counted(self) -> None:
        samples = tuple(float(index % 4) for index in range(35))
        noise = (1.0,) * 9
        mask = [True] * len(samples)
        mask[18] = False
        result = masked_event_matched_filter_snr(
            samples,
            1.0,
            noise,
            segment_length_samples=16,
            inclusion_mask=mask,
        )
        self.assertEqual(result.used_segment_starts, (0,))
        self.assertEqual(result.discarded_segment_starts, (16,))
        self.assertEqual(result.trailing_unsegmented_samples, 3)
        self.assertEqual(result.included_sample_count, 16)

    def test_no_complete_included_segment_and_wrong_psd_fail(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least one"):
            masked_event_matched_filter_snr(
                range(16),
                1.0,
                (1.0,) * 9,
                segment_length_samples=16,
                inclusion_mask=(False,) + (True,) * 15,
            )
        with self.assertRaisesRegex(ValueError, "equal length"):
            masked_event_matched_filter_snr(
                range(16),
                1.0,
                (1.0,) * 8,
                segment_length_samples=16,
            )

    def test_zero_signal_returns_zero(self) -> None:
        result = masked_event_matched_filter_snr(
            (0.0,) * 16,
            1.0,
            (1.0,) * 9,
            segment_length_samples=16,
        )
        self.assertEqual(result.matched_filter_snr, 0.0)


if __name__ == "__main__":
    unittest.main()
