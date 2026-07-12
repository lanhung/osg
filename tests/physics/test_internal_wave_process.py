"""Mass cancellation, periodicity, and scaling tests for a density dipole."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.processes import (  # noqa: E402
    oscillating_compensated_gaussian_dipole,
    regular_times,
)
from oceangravity.signal_processing import one_sided_spectrum  # noqa: E402


class TestCompensatedInternalWave(unittest.TestCase):
    def setUp(self) -> None:
        self.period = 30.0 * 60.0
        self.sample_count = 64
        self.interval = 2.0 * self.period / self.sample_count
        self.times = regular_times(self.sample_count, self.interval)

    def _result(self, **overrides: float):
        parameters = {
            "peak_density_anomaly_kg_m3": 0.5,
            "period_s": self.period,
            "phase_rad": 0.0,
            "horizontal_scale_m": 1_000.0,
            "vertical_scale_m": 100.0,
            "lobe_separation_m": 500.0,
            "dipole_center_xyz_m": (0.0, 0.0, -1_000.0),
            "observation_xyz_m": (0.0, 0.0, 0.0),
            "cells_per_axis": 6,
        }
        parameters.update(overrides)
        return oscillating_compensated_gaussian_dipole(self.times, **parameters)

    def test_discrete_lobe_masses_cancel_exactly(self) -> None:
        result = self._result()
        scale = result.positive_lobe_mass_per_unit_peak_density_m3
        self.assertAlmostEqual(
            result.net_mass_per_unit_peak_density_m3,
            0.0,
            delta=scale * 1.0e-15,
        )
        self.assertGreater(result.positive_lobe_mass_per_unit_peak_density_m3, 0.0)
        self.assertLess(result.negative_lobe_mass_per_unit_peak_density_m3, 0.0)

    def test_periodic_density_and_gravity_repeat_with_zero_mean(self) -> None:
        signal = self._result().signal
        samples_per_period = self.sample_count // 2
        for index in range(samples_per_period):
            self.assertAlmostEqual(
                signal.vertical_direct_gravity_m_s2[index],
                signal.vertical_direct_gravity_m_s2[index + samples_per_period],
                delta=signal.peak_absolute_gravity_m_s2 * 2e-15,
            )
        self.assertLess(
            abs(math.fsum(signal.vertical_direct_gravity_m_s2) / self.sample_count),
            signal.peak_absolute_gravity_m_s2 * 2e-15,
        )

    def test_spectrum_peaks_at_internal_wave_frequency(self) -> None:
        signal = self._result().signal
        spectrum = one_sided_spectrum(signal.vertical_direct_gravity_m_s2, self.interval)
        dominant_bin = max(
            range(1, len(spectrum.fourier_amplitude)),
            key=lambda index: abs(spectrum.fourier_amplitude[index]),
        )
        self.assertEqual(dominant_bin, 2)
        self.assertAlmostEqual(spectrum.frequencies_hz[dominant_bin], 1.0 / self.period)

    def test_density_amplitude_and_sign_scale_linearly(self) -> None:
        baseline = self._result().signal
        doubled = self._result(peak_density_anomaly_kg_m3=1.0).signal
        negative = self._result(peak_density_anomaly_kg_m3=-0.5).signal
        self.assertAlmostEqual(
            doubled.peak_absolute_gravity_m_s2,
            2.0 * baseline.peak_absolute_gravity_m_s2,
        )
        self.assertEqual(
            negative.vertical_direct_gravity_m_s2,
            tuple(-value for value in baseline.vertical_direct_gravity_m_s2),
        )

    def test_swapping_lobe_order_reverses_response(self) -> None:
        baseline = self._result()
        # Negative separation is deliberately invalid; phase pi performs the physical sign swap.
        swapped = self._result(phase_rad=math.pi)
        tolerance = baseline.signal.peak_absolute_gravity_m_s2 * 4e-15
        for original, reversed_value in zip(
            baseline.signal.vertical_direct_gravity_m_s2,
            swapped.signal.vertical_direct_gravity_m_s2,
            strict=True,
        ):
            self.assertAlmostEqual(
                reversed_value,
                -original,
                delta=tolerance,
            )

    def test_invalid_geometry_period_and_grid_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self._result(period_s=0.0)
        with self.assertRaises(ValueError):
            self._result(horizontal_scale_m=0.0)
        with self.assertRaises(ValueError):
            self._result(lobe_separation_m=0.0)
        with self.assertRaises(ValueError):
            self._result(cells_per_axis=True)


if __name__ == "__main__":
    unittest.main()
