"""Detrending, window-gain, ENBW, and windowed Parseval tests."""

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


class TestSpectralPreprocessing(unittest.TestCase):
    def test_periodic_hann_gains_and_enbw(self) -> None:
        spectrum = one_sided_spectrum([0.0] * 64, 1.0, window="hann-periodic")
        self.assertAlmostEqual(spectrum.window_coherent_gain, 0.5)
        self.assertAlmostEqual(spectrum.window_power_gain, 0.375)
        self.assertAlmostEqual(spectrum.equivalent_noise_bandwidth_bins, 1.5)

    def test_windowed_parseval_matches_normalized_weighted_mean_square(self) -> None:
        sample_count = 64
        samples = [
            2.0 * math.sin(2.0 * math.pi * 7 * index / sample_count) + 0.03 * index
            for index in range(sample_count)
        ]
        spectrum = one_sided_spectrum(samples, 0.25, window="hann-periodic")
        window_values = [
            0.5 - 0.5 * math.cos(2.0 * math.pi * index / sample_count)
            for index in range(sample_count)
        ]
        expected = math.fsum(
            (samples[index] * window_values[index]) ** 2 for index in range(sample_count)
        ) / (sample_count * spectrum.window_power_gain)
        self.assertAlmostEqual(
            mean_square_from_psd(spectrum), expected, delta=expected * 2.0e-14
        )

    def test_hann_coherent_gain_recovers_bin_sine_peak_amplitude(self) -> None:
        sample_count = 128
        interval = 0.5
        frequency_index = 9
        peak = 4.0
        samples = [
            peak * math.cos(2.0 * math.pi * frequency_index * index / sample_count)
            for index in range(sample_count)
        ]
        spectrum = one_sided_spectrum(samples, interval, window="hann-periodic")
        recovered_peak = (
            2.0
            * abs(spectrum.fourier_amplitude[frequency_index])
            / (spectrum.duration_s * spectrum.window_coherent_gain)
        )
        self.assertAlmostEqual(recovered_peak, peak, delta=peak * 2.0e-14)

    def test_constant_detrend_and_remove_mean_alias_match(self) -> None:
        samples = [3.0 + math.sin(index) for index in range(20)]
        explicit = one_sided_spectrum(samples, 1.0, detrend="constant")
        alias = one_sided_spectrum(samples, 1.0, remove_mean=True)
        self.assertEqual(explicit, alias)

    def test_linear_detrend_removes_affine_record(self) -> None:
        interval = 0.2
        intercept = 7.0
        slope = -0.4
        samples = [intercept + slope * index * interval for index in range(50)]
        spectrum = one_sided_spectrum(samples, interval, detrend="linear")
        self.assertAlmostEqual(spectrum.removed_linear_slope_per_s, slope, delta=1e-14)
        self.assertLess(mean_square_from_psd(spectrum), 1.0e-27)

    def test_invalid_window_detrend_and_ambiguous_mean_request(self) -> None:
        with self.assertRaises(ValueError):
            one_sided_spectrum([1.0, 2.0], 1.0, window="blackman")
        with self.assertRaises(ValueError):
            one_sided_spectrum([1.0, 2.0], 1.0, detrend="quadratic")
        with self.assertRaises(ValueError):
            one_sided_spectrum(
                [1.0, 2.0], 1.0, remove_mean=True, detrend="constant"
            )


if __name__ == "__main__":
    unittest.main()

