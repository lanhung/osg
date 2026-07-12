"""Time, gravity, and spectral tests for the periodic tide reference."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.constants import REFERENCE_SEAWATER_DENSITY
from oceangravity.gravity import disk_vertical_gravity_on_axis
from oceangravity.processes import periodic_disk_tide, regular_times
from oceangravity.signal_processing import one_sided_spectrum


class TestPeriodicDiskTide(unittest.TestCase):
    def setUp(self) -> None:
        self.period = 12.0 * 3600.0
        self.sample_count = 128
        self.interval = 2.0 * self.period / self.sample_count
        self.times = regular_times(self.sample_count, self.interval)

    def _signal(self, **overrides: float):
        parameters = {
            "sea_level_peak_amplitude_m": 1.5,
            "period_s": self.period,
            "phase_rad": 0.0,
            "disk_radius_m": 50_000.0,
            "disk_z_m": 0.0,
            "observation_z_m": 10_000.0,
        }
        parameters.update(overrides)
        return periodic_disk_tide(self.times, **parameters)

    def test_peak_matches_independent_unit_disk_gravity(self) -> None:
        signal = self._signal()
        unit_gravity = disk_vertical_gravity_on_axis(
            REFERENCE_SEAWATER_DENSITY.value,
            50_000.0,
            0.0,
            10_000.0,
        )
        self.assertAlmostEqual(signal.source_amplitude[0], 1.5)
        self.assertAlmostEqual(signal.vertical_direct_gravity_m_s2[0], 1.5 * unit_gravity)

    def test_full_cycles_have_negligible_mean_and_repeat(self) -> None:
        signal = self._signal()
        mean_sea_level = math.fsum(signal.source_amplitude) / self.sample_count
        scale = max(abs(value) for value in signal.source_amplitude)
        self.assertLess(abs(mean_sea_level), scale * 1.0e-15)
        samples_per_period = self.sample_count // 2
        for index in range(samples_per_period):
            self.assertAlmostEqual(
                signal.vertical_direct_gravity_m_s2[index],
                signal.vertical_direct_gravity_m_s2[index + samples_per_period],
                delta=signal.peak_absolute_gravity_m_s2 * 2.0e-15,
            )

    def test_frequency_peak_is_at_tidal_harmonic(self) -> None:
        signal = self._signal()
        spectrum = one_sided_spectrum(signal.vertical_direct_gravity_m_s2, self.interval)
        dominant_bin = max(
            range(1, len(spectrum.fourier_amplitude)),
            key=lambda index: abs(spectrum.fourier_amplitude[index]),
        )
        self.assertEqual(dominant_bin, 2)
        self.assertAlmostEqual(spectrum.frequencies_hz[dominant_bin], 1.0 / self.period)

    def test_amplitude_and_density_scale_linearly(self) -> None:
        baseline = self._signal()
        doubled_amplitude = self._signal(sea_level_peak_amplitude_m=3.0)
        doubled_density = periodic_disk_tide(
            self.times,
            sea_level_peak_amplitude_m=1.5,
            period_s=self.period,
            phase_rad=0.0,
            disk_radius_m=50_000.0,
            disk_z_m=0.0,
            observation_z_m=10_000.0,
            water_density_kg_m3=2.0 * REFERENCE_SEAWATER_DENSITY.value,
        )
        self.assertAlmostEqual(
            doubled_amplitude.peak_absolute_gravity_m_s2,
            2.0 * baseline.peak_absolute_gravity_m_s2,
        )
        self.assertAlmostEqual(
            doubled_density.peak_absolute_gravity_m_s2,
            2.0 * baseline.peak_absolute_gravity_m_s2,
        )

    def test_phase_shifts_source_and_gravity_together(self) -> None:
        signal = self._signal(phase_rad=math.pi / 2.0)
        self.assertAlmostEqual(signal.source_amplitude[0], 0.0, delta=1.0e-15)
        self.assertAlmostEqual(signal.vertical_direct_gravity_m_s2[0], 0.0, delta=1.0e-20)

    def test_invalid_period_density_and_time_axis_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self._signal(period_s=0.0)
        with self.assertRaises(ValueError):
            periodic_disk_tide(
                self.times,
                sea_level_peak_amplitude_m=1.0,
                period_s=self.period,
                phase_rad=0.0,
                disk_radius_m=1.0,
                disk_z_m=0.0,
                observation_z_m=1.0,
                water_density_kg_m3=0.0,
            )
        with self.assertRaises(ValueError):
            periodic_disk_tide(
                [0.0, 0.0],
                sea_level_peak_amplitude_m=1.0,
                period_s=self.period,
                phase_rad=0.0,
                disk_radius_m=1.0,
                disk_z_m=0.0,
                observation_z_m=1.0,
            )


if __name__ == "__main__":
    unittest.main()
