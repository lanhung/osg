"""Cross-check transient and periodic SNR under one-sided PSD conventions."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.signal_processing import (  # noqa: E402
    coherent_periodic_snr,
    matched_filter_snr,
    one_sided_spectrum,
)


class TestSignalToNoiseRatio(unittest.TestCase):
    def test_bin_sinusoid_matches_periodic_closed_form(self) -> None:
        sample_count = 256
        interval = 0.5
        frequency_index = 12
        peak_amplitude = 3.0e-8
        noise_psd = 2.5e-17
        samples = [
            peak_amplitude
            * math.sin(2.0 * math.pi * frequency_index * index / sample_count)
            for index in range(sample_count)
        ]
        spectrum = one_sided_spectrum(samples, interval)
        matched = matched_filter_snr(
            spectrum.frequencies_hz,
            spectrum.fourier_amplitude,
            [noise_psd] * len(spectrum.frequencies_hz),
        )
        periodic = coherent_periodic_snr(
            peak_amplitude, noise_psd, spectrum.duration_s
        )
        self.assertAlmostEqual(matched, periodic, delta=periodic * 2.0e-14)

    def test_snr_scaling_with_signal_noise_and_time(self) -> None:
        baseline = coherent_periodic_snr(2.0, 5.0, 7.0)
        self.assertAlmostEqual(coherent_periodic_snr(4.0, 5.0, 7.0), 2.0 * baseline)
        self.assertAlmostEqual(coherent_periodic_snr(2.0, 20.0, 7.0), 0.5 * baseline)
        self.assertAlmostEqual(coherent_periodic_snr(2.0, 5.0, 28.0), 2.0 * baseline)
        self.assertAlmostEqual(
            coherent_periodic_snr(2.0, 5.0, 14.0, coherent_fraction=0.5), baseline
        )

    def test_frequency_band_can_exclude_signal(self) -> None:
        sample_count = 64
        samples = [
            math.sin(2.0 * math.pi * 10 * index / sample_count)
            for index in range(sample_count)
        ]
        spectrum = one_sided_spectrum(samples, 1.0)
        result = matched_filter_snr(
            spectrum.frequencies_hz,
            spectrum.fourier_amplitude,
            [1.0] * len(spectrum.frequencies_hz),
            minimum_frequency_hz=spectrum.frequencies_hz[2],
            maximum_frequency_hz=spectrum.frequencies_hz[6],
        )
        self.assertLess(result, 1.0e-12)

    def test_zero_signal_has_zero_snr(self) -> None:
        self.assertEqual(
            matched_filter_snr([0.0, 1.0, 2.0], [0j, 0j, 0j], [1.0, 1.0, 1.0]),
            0.0,
        )

    def test_validation_rejects_invalid_psd_band_and_duration(self) -> None:
        with self.assertRaises(ValueError):
            matched_filter_snr([0.0, 1.0], [0j, 0j], [1.0, 0.0])
        with self.assertRaises(ValueError):
            matched_filter_snr(
                [0.0, 1.0],
                [0j, 0j],
                [1.0, 1.0],
                minimum_frequency_hz=2.0,
            )
        with self.assertRaises(ValueError):
            coherent_periodic_snr(1.0, 1.0, 0.0)
        with self.assertRaises(ValueError):
            coherent_periodic_snr(1.0, 1.0, 1.0, coherent_fraction=1.1)


if __name__ == "__main__":
    unittest.main()

