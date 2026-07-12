"""Mass, transition, gravity, and gradient tests for submarine mass relocation."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.processes import (
    mass_conserving_submarine_landslide,
    regular_times,
)


class TestSubmarineLandslide(unittest.TestCase):
    def setUp(self) -> None:
        self.times = regular_times(13, 1.0, start_time_s=-2.0)

    def _result(self, **overrides):
        parameters = {
            "solid_mass_kg": 1.0e12,
            "solid_source_xyz_m": (-1_000.0, 0.0, -2_000.0),
            "solid_destination_xyz_m": (2_000.0, 0.0, -3_000.0),
            "transition_start_s": 0.0,
            "transition_duration_s": 4.0,
            "observation_xyz_m": (0.0, 0.0, 1_000.0),
        }
        parameters.update(overrides)
        return mass_conserving_submarine_landslide(self.times, **parameters)

    def test_mass_anomaly_is_zero_and_end_states_are_exact(self) -> None:
        result = self._result()
        self.assertEqual(result.net_mass_anomaly_kg, 0.0)
        self.assertEqual(result.signal.source_amplitude[0], 0.0)
        self.assertEqual(result.signal.vertical_direct_gravity_m_s2[0], 0.0)
        final_index = self.times.index(4.0)
        self.assertEqual(result.signal.source_amplitude[final_index], 1.0)
        self.assertEqual(
            result.signal.vertical_direct_gravity_m_s2[final_index],
            result.final_gravity_change_m_s2[2],
        )

    def test_midpoint_is_half_complete_and_ramp_is_monotonic(self) -> None:
        result = self._result()
        midpoint = self.times.index(2.0)
        self.assertAlmostEqual(result.signal.source_amplitude[midpoint], 0.5)
        self.assertAlmostEqual(
            result.signal.vertical_direct_gravity_m_s2[midpoint],
            0.5 * result.final_gravity_change_m_s2[2],
        )
        self.assertTrue(
            all(
                right >= left
                for left, right in zip(
                    result.signal.source_amplitude[:-1],
                    result.signal.source_amplitude[1:],
                    strict=True,
                )
            )
        )

    def test_half_cosine_has_small_endpoint_increment_relative_to_middle(self) -> None:
        fine_times = regular_times(401, 0.01, start_time_s=0.0)
        result = mass_conserving_submarine_landslide(
            fine_times,
            solid_mass_kg=1.0,
            solid_source_xyz_m=(-1.0, 0.0, -2.0),
            solid_destination_xyz_m=(1.0, 0.0, -2.0),
            transition_start_s=0.0,
            transition_duration_s=4.0,
            observation_xyz_m=(0.0, 0.0, 1.0),
        )
        fractions = result.signal.source_amplitude
        first_increment = fractions[1] - fractions[0]
        middle_index = len(fractions) // 2
        middle_increment = fractions[middle_index + 1] - fractions[middle_index]
        self.assertLess(first_increment, 0.01 * middle_increment)

    def test_explicit_water_pair_adds_linearly_but_preserves_mass(self) -> None:
        solid_only = self._result()
        coupled = self._result(
            displaced_water_mass_kg=2.0e11,
            water_source_xyz_m=(0.0, -1_000.0, -500.0),
            water_destination_xyz_m=(0.0, 2_000.0, -500.0),
        )
        water_only_scaled = self._result(
            solid_mass_kg=2.0e11,
            solid_source_xyz_m=(0.0, -1_000.0, -500.0),
            solid_destination_xyz_m=(0.0, 2_000.0, -500.0),
        )
        for component in range(3):
            expected = math.fsum(
                (
                    solid_only.final_gravity_change_m_s2[component],
                    water_only_scaled.final_gravity_change_m_s2[component],
                )
            )
            self.assertEqual(coupled.final_gravity_change_m_s2[component], expected)
        self.assertEqual(coupled.net_mass_anomaly_kg, 0.0)

    def test_joint_translation_preserves_gravity_and_gradient(self) -> None:
        base = self._result()
        shift = (10_000.0, -20_000.0, 30_000.0)
        shifted = self._result(
            solid_source_xyz_m=tuple(
                value + shift[index] for index, value in enumerate((-1_000.0, 0.0, -2_000.0))
            ),
            solid_destination_xyz_m=tuple(
                value + shift[index] for index, value in enumerate((2_000.0, 0.0, -3_000.0))
            ),
            observation_xyz_m=tuple(
                value + shift[index] for index, value in enumerate((0.0, 0.0, 1_000.0))
            ),
        )
        self.assertEqual(base.final_gravity_change_m_s2, shifted.final_gravity_change_m_s2)
        self.assertEqual(
            base.final_gravity_gradient_change_s2,
            shifted.final_gravity_gradient_change_s2,
        )

    def test_far_field_acceleration_has_dipole_like_decay(self) -> None:
        source = (-100.0, 0.0, 0.0)
        destination = (100.0, 0.0, 0.0)
        near = self._result(
            solid_source_xyz_m=source,
            solid_destination_xyz_m=destination,
            observation_xyz_m=(1_000.0, 0.0, 0.0),
        ).final_gravity_change_m_s2[0]
        far = self._result(
            solid_source_xyz_m=source,
            solid_destination_xyz_m=destination,
            observation_xyz_m=(2_000.0, 0.0, 0.0),
        ).final_gravity_change_m_s2[0]
        ratio = abs(near / far)
        self.assertGreater(ratio, 6.0)
        self.assertLess(ratio, 11.0)

    def test_invalid_mass_duration_and_water_coordinates_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self._result(solid_mass_kg=0.0)
        with self.assertRaises(ValueError):
            self._result(transition_duration_s=0.0)
        with self.assertRaises(ValueError):
            self._result(displaced_water_mass_kg=-1.0)
        with self.assertRaises(ValueError):
            self._result(displaced_water_mass_kg=1.0)


if __name__ == "__main__":
    unittest.main()
