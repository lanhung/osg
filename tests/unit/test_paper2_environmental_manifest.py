"""Physical-role and double-counting gates for Paper 2 products."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class TestPaper2EnvironmentalManifest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads(
            (ROOT / "data/manifests/paper2_environmental_products.json").read_text()
        )

    def test_products_are_versioned_and_cited(self) -> None:
        products = {item["id"]: item for item in self.document["products"]}
        self.assertEqual(products["era5-single-levels-hourly"]["doi"], "10.24381/cds.adbb2d47")
        self.assertEqual(
            products["cmems-global-ocean-physics-analysis-forecast"]["doi"],
            "10.48670/moi-00016",
        )
        self.assertEqual(
            products["cmems-global-ocean-physics-analysis-forecast"]["dataset_id"],
            "cmems_mod_glo_phy_anfc_merged-sl_PT1H-i",
        )

    def test_wave_height_is_never_a_mass_load(self) -> None:
        era5 = self.document["products"][0]
        wave = next(
            variable
            for variable in era5["variables"]
            if variable["name"] == "significant_height_of_combined_wind_waves_and_swell"
        )
        self.assertFalse(wave["mass_load_eligible"])
        self.assertIn("not an additional mean water-mass load", " ".join(era5["warnings"]))

    def test_double_count_gate_is_closed_by_component_selection(self) -> None:
        self.assertEqual(
            self.document["double_count_gate"]["status"],
            "closed-by-explicit-variable-selection",
        )
        cmems = self.document["products"][1]
        self.assertEqual(cmems["selected_variable"], "sea_surface_height")
        self.assertTrue(cmems["variable_metadata_status"].startswith("verified"))


if __name__ == "__main__":
    unittest.main()
