"""Local hydrology Bouguer-slab baseline tests."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.constants import GRAVITATIONAL_CONSTANT
from oceangravity.loading import (
    groundwater_level_to_equivalent_water_height,
    water_equivalent_height_to_bouguer_slab_gravity,
)


class TestHydrologySlab(unittest.TestCase):
    def test_groundwater_porosity_conversion_is_linear(self) -> None:
        self.assertEqual(
            groundwater_level_to_equivalent_water_height((1.0, -2.0, 0.0), 0.05),
            (0.05, -0.1, 0.0),
        )

    def test_positive_storage_below_observer_has_negative_local_up_gravity(self) -> None:
        result = water_equivalent_height_to_bouguer_slab_gravity((1.0, -0.5))
        expected = 2.0 * math.pi * GRAVITATIONAL_CONSTANT.value * 1_000.0
        self.assertAlmostEqual(result[0], -expected)
        self.assertAlmostEqual(result[1], 0.5 * expected)

    def test_load_above_observer_reverses_direction(self) -> None:
        below = water_equivalent_height_to_bouguer_slab_gravity((0.1,))
        above = water_equivalent_height_to_bouguer_slab_gravity((0.1,), load_below_observer=False)
        self.assertEqual(above[0], -below[0])

    def test_one_millimetre_water_is_about_0042_microgal(self) -> None:
        result = water_equivalent_height_to_bouguer_slab_gravity((0.001,))[0]
        self.assertAlmostEqual(abs(result) / 1.0e-8, 0.04193586, places=8)

    def test_invalid_porosity_density_and_boolean_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "porosity"):
            groundwater_level_to_equivalent_water_height((1.0,), 1.1)
        with self.assertRaisesRegex(ValueError, "density"):
            water_equivalent_height_to_bouguer_slab_gravity((1.0,), water_density_kg_m3=0.0)
        with self.assertRaisesRegex(ValueError, "boolean"):
            water_equivalent_height_to_bouguer_slab_gravity(
                (1.0,),
                load_below_observer=1,  # type: ignore[arg-type]
            )


if __name__ == "__main__":
    unittest.main()
