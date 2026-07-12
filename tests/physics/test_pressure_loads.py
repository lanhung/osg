"""Hydrostatic pressure-load conversion and inverse-barometer closure tests."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.constants import STANDARD_GRAVITY
from oceangravity.loading import (
    inverse_barometer_sea_level_anomaly,
    pressure_anomaly_to_column_surface_density,
)


class TestPressureLoads(unittest.TestCase):
    def test_pressure_column_conversion_preserves_sign_and_missingness(self) -> None:
        gravity = STANDARD_GRAVITY.value
        result = pressure_anomaly_to_column_surface_density(
            ((gravity, -2.0 * gravity, None, math.nan),)
        )
        self.assertEqual(result, ((1.0, -2.0, None, None),))

    def test_inverse_barometer_sign_and_area_weighted_mass_closure(self) -> None:
        result = inverse_barometer_sea_level_anomaly(
            ((-300.0, 100.0),),
            ((1.0, 3.0),),
            water_density_kg_m3=1_000.0,
            gravity_m_s2=10.0,
        )
        self.assertEqual(result.ocean_mean_pressure_anomaly_pa, 0.0)
        self.assertEqual(result.sea_level_anomaly_m, ((0.03, -0.01),))
        self.assertAlmostEqual(result.net_surface_mass_anomaly_kg, 0.0)
        self.assertEqual(result.included_area_m2, 4.0)

    def test_uniform_pressure_is_removed_as_domain_mean(self) -> None:
        result = inverse_barometer_sea_level_anomaly(
            ((125.0, 125.0), (125.0, 125.0)),
            ((1.0, 2.0), (3.0, 4.0)),
        )
        self.assertEqual(result.ocean_mean_pressure_anomaly_pa, 125.0)
        self.assertEqual(result.sea_level_anomaly_m, ((-0.0, -0.0), (-0.0, -0.0)))
        self.assertEqual(result.net_surface_mass_anomaly_kg, 0.0)

    def test_mask_fraction_and_missing_skip_are_audited(self) -> None:
        result = inverse_barometer_sea_level_anomaly(
            ((-100.0, None), (100.0, 999.0)),
            ((2.0, 3.0), (2.0, 5.0)),
            ocean_mask=((True, True), (True, False)),
            cell_ocean_fraction=((0.5, 1.0), (0.5, 1.0)),
            missing_policy="skip",
        )
        self.assertEqual(result.included_area_m2, 2.0)
        self.assertEqual(result.ocean_mean_pressure_anomaly_pa, 0.0)
        self.assertEqual(result.sea_level_anomaly_m[0][1], None)
        self.assertEqual(result.sea_level_anomaly_m[1][1], None)
        self.assertAlmostEqual(result.net_surface_mass_anomaly_kg, 0.0)

    def test_no_mean_removal_exposes_open_domain_mass_change(self) -> None:
        result = inverse_barometer_sea_level_anomaly(
            ((100.0,),),
            ((2.0,),),
            water_density_kg_m3=1_000.0,
            gravity_m_s2=10.0,
            remove_ocean_mean=False,
        )
        self.assertEqual(result.sea_level_anomaly_m, ((-0.01,),))
        self.assertEqual(result.net_surface_mass_anomaly_kg, -20.0)

    def test_invalid_or_missing_domain_inputs_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "missing"):
            inverse_barometer_sea_level_anomaly(((None,),), ((1.0,),))
        with self.assertRaisesRegex(ValueError, "fraction"):
            inverse_barometer_sea_level_anomaly(((1.0,),), ((1.0,),), cell_ocean_fraction=((1.1,),))
        with self.assertRaisesRegex(ValueError, "shape"):
            inverse_barometer_sea_level_anomaly(((1.0,),), ((1.0, 2.0),))


if __name__ == "__main__":
    unittest.main()
