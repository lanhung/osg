"""Mass balance, translation, sign, and far-field tests for the 3-D eddy."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.processes import (
    translating_compensated_gaussian_density_eddy,
)


class TestCompensatedDensityEddy(unittest.TestCase):
    def _result(self, **overrides):
        parameters = {
            "peak_core_density_anomaly_kg_m3": 0.5,
            "core_horizontal_scale_m": 10_000.0,
            "halo_horizontal_scale_m": 25_000.0,
            "vertical_scale_m": 500.0,
            "translation_speed_x_m_s": 0.5,
            "closest_approach_y_m": 0.0,
            "passage_time_s": 0.0,
            "center_z_m": -2_000.0,
            "observation_xyz_m": (0.0, 0.0, 10_000.0),
            "cells_per_axis": 5,
        }
        parameters.update(overrides)
        return translating_compensated_gaussian_density_eddy(
            (-40_000.0, -20_000.0, 0.0, 20_000.0, 40_000.0),
            **parameters,
        )

    def test_discrete_core_and_halo_mass_cancel(self) -> None:
        result = self._result()
        scale = result.positive_mass_per_unit_core_density_m3
        self.assertAlmostEqual(
            result.net_mass_per_unit_core_density_m3,
            0.0,
            delta=scale * 2e-15,
        )
        self.assertGreater(result.halo_density_scale_relative_to_core, 0.0)
        self.assertLess(result.halo_density_scale_relative_to_core, 1.0)

    def test_central_translation_is_time_symmetric(self) -> None:
        signal = self._result().signal
        self.assertAlmostEqual(
            signal.vertical_direct_gravity_m_s2[0],
            signal.vertical_direct_gravity_m_s2[-1],
            delta=max(abs(signal.vertical_direct_gravity_m_s2[0]), 1e-30) * 2e-13,
        )
        self.assertAlmostEqual(
            signal.vertical_direct_gravity_gradient_s2[1],
            signal.vertical_direct_gravity_gradient_s2[-2],
            delta=max(abs(signal.vertical_direct_gravity_gradient_s2[1]), 1e-30) * 2e-13,
        )

    def test_density_sign_reverses_gravity_and_gradient(self) -> None:
        positive = self._result().signal
        negative = self._result(peak_core_density_anomaly_kg_m3=-0.5).signal
        self.assertEqual(
            negative.vertical_direct_gravity_m_s2,
            tuple(-value for value in positive.vertical_direct_gravity_m_s2),
        )
        self.assertEqual(
            negative.vertical_direct_gravity_gradient_s2,
            tuple(-value for value in positive.vertical_direct_gravity_gradient_s2),
        )

    def test_far_field_is_strongly_suppressed(self) -> None:
        near = self._result(observation_xyz_m=(0.0, 0.0, 20_000.0)).signal
        far = self._result(observation_xyz_m=(0.0, 0.0, 500_000.0)).signal
        self.assertLess(
            far.peak_absolute_gravity_m_s2,
            near.peak_absolute_gravity_m_s2 * 1e-3,
        )

    def test_invalid_halo_and_speed_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self._result(halo_horizontal_scale_m=10_000.0)
        with self.assertRaises(ValueError):
            self._result(translation_speed_x_m_s=0.0)


if __name__ == "__main__":
    unittest.main()
