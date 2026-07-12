"""Time, mass, sign, geometry, and partial-cell tests for gridded SSH signals."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.processes import gridded_sea_level_direct_gravity_signal  # noqa: E402


class TestGriddedSeaLevelSignal(unittest.TestCase):
    def _result(self, geometry="wgs84", **overrides):
        parameters = {
            "times_s": (0.0, 3600.0, 7200.0),
            "sea_level_anomaly_m": (
                ((0.0, 0.0), (0.0, 0.0)),
                ((0.5, 0.5), (0.5, 0.5)),
                ((-1.0, -1.0), (-1.0, -1.0)),
            ),
            "latitude_edges_deg": (18.0, 20.0, 22.0),
            "longitude_edges_deg_unwrapped": (108.0, 110.0, 112.0),
            "observation_latitude_deg": 20.0,
            "observation_longitude_deg": 110.0,
            "observation_height_m": 100_000.0,
            "geometry": geometry,
        }
        parameters.update(overrides)
        return gridded_sea_level_direct_gravity_signal(**parameters)

    def test_amplitude_sign_and_mass_scale_linearly(self) -> None:
        result = self._result()
        self.assertEqual(result.signal.vertical_direct_gravity_m_s2[0], 0.0)
        self.assertAlmostEqual(
            result.signal.vertical_direct_gravity_m_s2[2],
            -2.0 * result.signal.vertical_direct_gravity_m_s2[1],
        )
        self.assertAlmostEqual(result.included_mass_kg[2], -2.0 * result.included_mass_kg[1])
        self.assertEqual(len(set(result.included_area_m2)), 1)

    def test_partial_cells_scale_mass_and_zero_land_may_be_missing(self) -> None:
        result = self._result(
            sea_level_anomaly_m=(
                ((1.0, None), (1.0, 1.0)),
                ((1.0, None), (1.0, 1.0)),
                ((1.0, None), (1.0, 1.0)),
            ),
            cell_load_fraction=((1.0, 0.0), (0.5, 1.0)),
        )
        self.assertEqual(result.included_mass_kg[0], result.included_mass_kg[1])
        self.assertGreater(result.included_mass_kg[0], 0.0)

    def test_spherical_and_wgs84_paths_are_distinct_but_close(self) -> None:
        sphere = self._result("sphere")
        ellipsoid = self._result("wgs84")
        self.assertNotEqual(
            sphere.signal.vertical_direct_gravity_m_s2[1],
            ellipsoid.signal.vertical_direct_gravity_m_s2[1],
        )
        relative = abs(
            sphere.signal.vertical_direct_gravity_m_s2[1]
            - ellipsoid.signal.vertical_direct_gravity_m_s2[1]
        ) / abs(ellipsoid.signal.vertical_direct_gravity_m_s2[1])
        self.assertLess(relative, 0.01)

    def test_time_and_geometry_validation(self) -> None:
        with self.assertRaises(ValueError):
            self._result(times_s=(0.0, 0.0, 1.0))
        with self.assertRaises(ValueError):
            self._result(geometry="flat")


if __name__ == "__main__":
    unittest.main()
