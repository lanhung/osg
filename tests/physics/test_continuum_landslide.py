"""Mass, transition, and point-limit tests for the Gaussian continuum slide."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.processes import (  # noqa: E402
    mass_conserving_gaussian_submarine_landslide,
    mass_conserving_submarine_landslide,
)


class TestContinuumLandslide(unittest.TestCase):
    def _result(self, **overrides):
        parameters = {
            "solid_mass_kg": 1e12,
            "horizontal_scale_m": 200.0,
            "vertical_scale_m": 100.0,
            "solid_source_xyz_m": (-1_000.0, 0.0, -2_000.0),
            "solid_destination_xyz_m": (2_000.0, 0.0, -3_000.0),
            "transition_start_s": 0.0,
            "transition_duration_s": 4.0,
            "observation_xyz_m": (0.0, 0.0, 10_000.0),
            "cells_per_axis": 6,
        }
        parameters.update(overrides)
        return mass_conserving_gaussian_submarine_landslide(
            (-1.0, 0.0, 2.0, 4.0, 5.0), **parameters
        )

    def test_discrete_continuum_mass_is_conserved(self) -> None:
        result = self._result()
        self.assertAlmostEqual(result.net_mass_anomaly_kg, 0.0, delta=1e12 * 2e-15)
        self.assertEqual(result.signal.source_amplitude[:2], (0.0, 0.0))
        self.assertAlmostEqual(result.signal.source_amplitude[2], 0.5)
        self.assertEqual(result.signal.source_amplitude[3:], (1.0, 1.0))
        self.assertIsNotNone(result.signal.vertical_direct_gravity_gradient_s2)

    def test_narrow_continuum_approaches_point_pair_at_long_distance(self) -> None:
        continuum = self._result(
            horizontal_scale_m=20.0,
            vertical_scale_m=10.0,
            observation_xyz_m=(0.0, 0.0, 100_000.0),
        )
        point = mass_conserving_submarine_landslide(
            (-1.0, 0.0, 2.0, 4.0, 5.0),
            solid_mass_kg=1e12,
            solid_source_xyz_m=(-1_000.0, 0.0, -2_000.0),
            solid_destination_xyz_m=(2_000.0, 0.0, -3_000.0),
            transition_start_s=0.0,
            transition_duration_s=4.0,
            observation_xyz_m=(0.0, 0.0, 100_000.0),
        )
        for actual, expected in zip(
            continuum.final_gravity_change_m_s2,
            point.final_gravity_change_m_s2,
            strict=True,
        ):
            self.assertAlmostEqual(
                actual,
                expected,
                delta=max(abs(expected), 1e-30) * 2e-6,
            )

    def test_joint_translation_is_invariant(self) -> None:
        base = self._result()
        shift = (10_000.0, -20_000.0, 30_000.0)
        shifted = self._result(
            solid_source_xyz_m=tuple(
                value + shift[index]
                for index, value in enumerate((-1_000.0, 0.0, -2_000.0))
            ),
            solid_destination_xyz_m=tuple(
                value + shift[index]
                for index, value in enumerate((2_000.0, 0.0, -3_000.0))
            ),
            observation_xyz_m=tuple(
                value + shift[index]
                for index, value in enumerate((0.0, 0.0, 10_000.0))
            ),
        )
        for actual, expected in zip(
            shifted.final_gravity_change_m_s2,
            base.final_gravity_change_m_s2,
            strict=True,
        ):
            self.assertAlmostEqual(actual, expected, delta=max(abs(expected), 1e-30) * 2e-14)

    def test_invalid_scales_and_grid_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self._result(horizontal_scale_m=0.0)
        with self.assertRaises(ValueError):
            self._result(cells_per_axis=1)


if __name__ == "__main__":
    unittest.main()
