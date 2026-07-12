"""Source-shape and gravity tests for the storm-surge reference model."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.constants import REFERENCE_SEAWATER_DENSITY
from oceangravity.gravity import disk_vertical_gravity_on_axis
from oceangravity.processes import (
    asymmetric_gaussian_disk_surge,
    regular_times,
)
from oceangravity.signal_processing import one_sided_spectrum


class TestStormSurgeProcess(unittest.TestCase):
    def setUp(self) -> None:
        self.hour = 3600.0
        self.interval = 300.0
        # Six rise scales before and six fall scales after the peak.
        self.times = regular_times(505, self.interval, start_time_s=-12.0 * self.hour)

    def _signal(self, **overrides: float):
        parameters = {
            "peak_sea_level_anomaly_m": 2.0,
            "peak_time_s": 0.0,
            "rise_scale_s": 2.0 * self.hour,
            "fall_scale_s": 5.0 * self.hour,
            "disk_radius_m": 80_000.0,
            "disk_z_m": 0.0,
            "observation_z_m": 20_000.0,
        }
        parameters.update(overrides)
        return asymmetric_gaussian_disk_surge(self.times, **parameters)

    def test_peak_matches_independent_disk_response(self) -> None:
        signal = self._signal()
        peak_index = self.times.index(0.0)
        expected_unit = disk_vertical_gravity_on_axis(
            REFERENCE_SEAWATER_DENSITY.value,
            80_000.0,
            0.0,
            20_000.0,
        )
        self.assertEqual(signal.source_amplitude[peak_index], 2.0)
        self.assertEqual(signal.vertical_direct_gravity_m_s2[peak_index], 2.0 * expected_unit)

    def test_rise_and_fall_scales_are_independent(self) -> None:
        signal = self._signal()
        before = signal.source_amplitude[self.times.index(-2.0 * self.hour)]
        after = signal.source_amplitude[self.times.index(5.0 * self.hour)]
        expected = 2.0 * math.exp(-0.5)
        self.assertAlmostEqual(before, expected)
        self.assertAlmostEqual(after, expected)
        one_hour_before = signal.source_amplitude[self.times.index(-1.0 * self.hour)]
        one_hour_after = signal.source_amplitude[self.times.index(1.0 * self.hour)]
        self.assertLess(one_hour_before, one_hour_after)

    def test_numerical_event_integral_matches_analytic_area(self) -> None:
        signal = self._signal()
        trapezoids = [
            0.5
            * self.interval
            * (signal.source_amplitude[index] + signal.source_amplitude[index + 1])
            for index in range(len(signal.source_amplitude) - 1)
        ]
        numerical_integral = math.fsum(trapezoids)
        expected = 2.0 * math.sqrt(math.pi / 2.0) * (2.0 * self.hour + 5.0 * self.hour)
        self.assertLess(abs(numerical_integral - expected) / expected, 1.0e-5)

    def test_signal_is_broadband_not_a_single_spectral_line(self) -> None:
        signal = self._signal()
        spectrum = one_sided_spectrum(
            signal.vertical_direct_gravity_m_s2,
            self.interval,
            detrend="constant",
        )
        positive_bins = sorted(
            (abs(value) for value in spectrum.fourier_amplitude[1:]), reverse=True
        )
        self.assertGreater(positive_bins[1], 0.05 * positive_bins[0])

    def test_amplitude_density_and_sign_scale_linearly(self) -> None:
        baseline = self._signal()
        negative = self._signal(peak_sea_level_anomaly_m=-2.0)
        doubled_density = asymmetric_gaussian_disk_surge(
            self.times,
            peak_sea_level_anomaly_m=2.0,
            peak_time_s=0.0,
            rise_scale_s=2.0 * self.hour,
            fall_scale_s=5.0 * self.hour,
            disk_radius_m=80_000.0,
            disk_z_m=0.0,
            observation_z_m=20_000.0,
            water_density_kg_m3=2.0 * REFERENCE_SEAWATER_DENSITY.value,
        )
        self.assertEqual(
            negative.vertical_direct_gravity_m_s2,
            tuple(-value for value in baseline.vertical_direct_gravity_m_s2),
        )
        self.assertAlmostEqual(
            doubled_density.peak_absolute_gravity_m_s2,
            2.0 * baseline.peak_absolute_gravity_m_s2,
        )

    def test_invalid_timescales_and_density_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self._signal(rise_scale_s=0.0)
        with self.assertRaises(ValueError):
            asymmetric_gaussian_disk_surge(
                self.times,
                peak_sea_level_anomaly_m=1.0,
                peak_time_s=0.0,
                rise_scale_s=1.0,
                fall_scale_s=1.0,
                disk_radius_m=1.0,
                disk_z_m=0.0,
                observation_z_m=1.0,
                water_density_kg_m3=-1.0,
            )


if __name__ == "__main__":
    unittest.main()
