"""Fourier normalization and Parseval tests for the reference spectrum."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.signal_processing import (  # noqa: E402
    mean_square_from_psd,
    one_sided_spectrum,
)


class TestOneSidedSpectrum(unittest.TestCase):
    def test_parseval_for_even_and_odd_record_lengths(self) -> None:
        for sample_count in (31, 32):
            samples = [
                0.7 * math.sin(2.0 * math.pi * 3 * index / sample_count)
                + 0.2 * math.cos(2.0 * math.pi * 5 * index / sample_count)
                + 0.03 * index
                for index in range(sample_count)
            ]
            spectrum = one_sided_spectrum(samples, 0.25)
            expected_mean_square = math.fsum(value * value for value in samples) / sample_count
            self.assertAlmostEqual(
                mean_square_from_psd(spectrum),
                expected_mean_square,
                delta=expected_mean_square * 2.0e-14,
            )

    def test_bin_centred_sine_amplitude_and_mean_square(self) -> None:
        sample_count = 128
        interval = 0.5
        frequency_index = 8
        amplitude = 3.0
        samples = [
            amplitude * math.sin(2.0 * math.pi * frequency_index * index / sample_count)
            for index in range(sample_count)
        ]
        spectrum = one_sided_spectrum(samples, interval)
        duration = sample_count * interval
        self.assertAlmostEqual(
            abs(spectrum.fourier_amplitude[frequency_index]),
            amplitude * duration / 2.0,
            delta=amplitude * duration * 1.0e-14,
        )
        self.assertAlmostEqual(
            mean_square_from_psd(spectrum),
            amplitude**2 / 2.0,
            delta=amplitude**2 * 1.0e-14,
        )

    def test_constant_is_dc_and_mean_removal_is_explicit(self) -> None:
        samples = [4.0] * 16
        raw = one_sided_spectrum(samples, 2.0)
        centred = one_sided_spectrum(samples, 2.0, remove_mean=True)
        self.assertEqual(raw.fourier_amplitude[0], 4.0 * 16 * 2.0)
        self.assertTrue(all(abs(value) < 1.0e-12 for value in raw.fourier_amplitude[1:]))
        self.assertEqual(centred.removed_mean, 4.0)
        self.assertEqual(mean_square_from_psd(centred), 0.0)

    def test_frequency_axis_and_nyquist_for_even_record(self) -> None:
        spectrum = one_sided_spectrum([0.0] * 8, 0.25)
        self.assertEqual(spectrum.duration_s, 2.0)
        self.assertEqual(spectrum.frequency_spacing_hz, 0.5)
        self.assertEqual(spectrum.frequencies_hz, (0.0, 0.5, 1.0, 1.5, 2.0))

    def test_input_validation(self) -> None:
        with self.assertRaises(ValueError):
            one_sided_spectrum([1.0], 1.0)
        with self.assertRaises(ValueError):
            one_sided_spectrum([1.0, 2.0], 0.0)
        with self.assertRaises(ValueError):
            one_sided_spectrum([1.0, math.nan], 1.0)


if __name__ == "__main__":
    unittest.main()

