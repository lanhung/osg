"""Mass, propagation, timing, and sign tests for the tsunami wave packet."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.constants import STANDARD_GRAVITY
from oceangravity.processes import (
    propagating_compensated_gaussian_tsunami,
    regular_times,
)


class TestTsunamiWavePacket(unittest.TestCase):
    def setUp(self) -> None:
        self.scale = 20_000.0
        self.separation = 4.0 * self.scale
        self.depth = 4_000.0
        self.speed = math.sqrt(STANDARD_GRAVITY.value * self.depth)
        self.characteristic_time = self.scale / self.speed
        self.interval = self.characteristic_time / 4.0
        self.times = regular_times(49, self.interval, start_time_s=-4.0 * self.characteristic_time)

    def _result(self, **overrides: float):
        parameters = {
            "crest_peak_sea_level_m": 1.0,
            "horizontal_scale_m": self.scale,
            "crest_trough_separation_m": self.separation,
            "water_depth_m": self.depth,
            "crest_passage_time_s": 0.0,
            "wave_plane_z_m": 0.0,
            "observation_xyz_m": (0.0, 0.0, 10_000.0),
            "radial_cells": 32,
            "angular_cells": 48,
        }
        parameters.update(overrides)
        return propagating_compensated_gaussian_tsunami(self.times, **parameters)

    def test_phase_speed_matches_shallow_water_relation(self) -> None:
        result = self._result()
        self.assertEqual(result.shallow_water_phase_speed_m_s, self.speed)

    def test_integrated_crest_and_trough_mass_cancel(self) -> None:
        result = self._result()
        self.assertGreater(result.crest_mass_amplitude_kg, 0.0)
        self.assertEqual(result.trough_mass_amplitude_kg, -result.crest_mass_amplitude_kg)
        self.assertEqual(result.net_surface_mass_amplitude_kg, 0.0)

    def test_crest_and_trough_arrival_times_and_signs(self) -> None:
        result = self._result()
        crest_index = self.times.index(0.0)
        trough_time = self.separation / self.speed
        trough_index = min(
            range(len(self.times)), key=lambda index: abs(self.times[index] - trough_time)
        )
        self.assertGreater(result.signal.source_amplitude[crest_index], 0.99)
        self.assertLess(result.signal.source_amplitude[trough_index], -0.99)
        self.assertLess(result.signal.vertical_direct_gravity_m_s2[crest_index], 0.0)
        self.assertGreater(result.signal.vertical_direct_gravity_m_s2[trough_index], 0.0)

    def test_deeper_water_increases_speed_and_shortens_passage_scale(self) -> None:
        baseline = self._result()
        deeper = self._result(water_depth_m=4.0 * self.depth)
        self.assertAlmostEqual(
            deeper.shallow_water_phase_speed_m_s,
            2.0 * baseline.shallow_water_phase_speed_m_s,
        )

    def test_amplitude_and_density_scale_linearly(self) -> None:
        baseline = self._result()
        negative = self._result(crest_peak_sea_level_m=-1.0)
        doubled = self._result(water_density_kg_m3=2_050.0)
        self.assertEqual(
            negative.signal.vertical_direct_gravity_m_s2,
            tuple(-value for value in baseline.signal.vertical_direct_gravity_m_s2),
        )
        self.assertAlmostEqual(
            doubled.signal.peak_absolute_gravity_m_s2,
            2.0 * baseline.signal.peak_absolute_gravity_m_s2,
        )

    def test_invalid_depth_scale_separation_and_observation_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self._result(water_depth_m=0.0)
        with self.assertRaises(ValueError):
            self._result(horizontal_scale_m=0.0)
        with self.assertRaises(ValueError):
            self._result(crest_trough_separation_m=0.0)
        with self.assertRaises(ValueError):
            self._result(observation_xyz_m=(0.0, 0.0))


if __name__ == "__main__":
    unittest.main()
