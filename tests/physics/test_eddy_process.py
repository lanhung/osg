"""Translation, symmetry, and scaling tests for the Gaussian surface eddy."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.constants import REFERENCE_SEAWATER_DENSITY
from oceangravity.processes import (
    regular_times,
    translating_gaussian_surface_eddy,
)


class TestTranslatingGaussianEddy(unittest.TestCase):
    def setUp(self) -> None:
        self.scale = 20_000.0
        self.speed = 0.5
        self.characteristic_time = self.scale / self.speed
        self.interval = self.characteristic_time / 5.0
        self.times = regular_times(41, self.interval, start_time_s=-4.0 * self.characteristic_time)

    def _signal(self, **overrides: float):
        parameters = {
            "peak_sea_level_anomaly_m": 0.4,
            "horizontal_scale_m": self.scale,
            "translation_speed_x_m_s": self.speed,
            "closest_approach_y_m": 0.0,
            "passage_time_s": 0.0,
            "anomaly_z_m": 0.0,
            "observation_xyz_m": (0.0, 0.0, 10_000.0),
            "radial_cells": 32,
            "angular_cells": 48,
        }
        parameters.update(overrides)
        return translating_gaussian_surface_eddy(self.times, **parameters)

    def test_central_passage_peaks_at_passage_time(self) -> None:
        signal = self._signal()
        peak_index = self.times.index(0.0)
        self.assertEqual(signal.source_amplitude[peak_index], 0.4)
        self.assertEqual(
            abs(signal.vertical_direct_gravity_m_s2[peak_index]),
            signal.peak_absolute_gravity_m_s2,
        )

    def test_characteristic_translation_time_matches_gaussian_scale(self) -> None:
        signal = self._signal()
        expected = 0.4 * math.exp(-0.5)
        before = signal.source_amplitude[self.times.index(-self.characteristic_time)]
        after = signal.source_amplitude[self.times.index(self.characteristic_time)]
        self.assertAlmostEqual(before, expected)
        self.assertAlmostEqual(after, expected)

    def test_vertical_gravity_is_time_symmetric_for_central_passage(self) -> None:
        signal = self._signal()
        centre_index = self.times.index(0.0)
        for offset in range(1, min(centre_index, len(self.times) - centre_index)):
            before = signal.vertical_direct_gravity_m_s2[centre_index - offset]
            after = signal.vertical_direct_gravity_m_s2[centre_index + offset]
            self.assertAlmostEqual(
                before,
                after,
                delta=max(abs(before), abs(after), 1e-30) * 3e-14,
            )

    def test_nonzero_closest_approach_reduces_local_peak(self) -> None:
        central = self._signal()
        offset = self._signal(closest_approach_y_m=self.scale)
        peak_index = self.times.index(0.0)
        self.assertAlmostEqual(
            offset.source_amplitude[peak_index],
            central.source_amplitude[peak_index] * math.exp(-0.5),
        )
        self.assertLess(
            offset.peak_absolute_gravity_m_s2,
            central.peak_absolute_gravity_m_s2,
        )

    def test_peak_density_and_sign_scale_gravity_linearly(self) -> None:
        baseline = self._signal()
        negative = self._signal(peak_sea_level_anomaly_m=-0.4)
        doubled_density = self._signal(water_density_kg_m3=2.0 * REFERENCE_SEAWATER_DENSITY.value)
        self.assertEqual(
            negative.vertical_direct_gravity_m_s2,
            tuple(-value for value in baseline.vertical_direct_gravity_m_s2),
        )
        self.assertAlmostEqual(
            doubled_density.peak_absolute_gravity_m_s2,
            2.0 * baseline.peak_absolute_gravity_m_s2,
        )

    def test_invalid_scale_speed_density_and_observation_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self._signal(horizontal_scale_m=0.0)
        with self.assertRaises(ValueError):
            self._signal(translation_speed_x_m_s=0.0)
        with self.assertRaises(ValueError):
            self._signal(water_density_kg_m3=0.0)
        with self.assertRaises(ValueError):
            self._signal(observation_xyz_m=(0.0, 0.0))


if __name__ == "__main__":
    unittest.main()
