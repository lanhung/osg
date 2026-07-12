"""Source and arrival-binding tests for Manila scenarios."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from oceangravity.pegs import ManilaScenario, TsunamiArrival  # noqa: E402


def _scenario(**overrides) -> ManilaScenario:
    values = {
        "scenario_id": "fixture-north-mw86",
        "segment": "north",
        "moment_magnitude": 8.6,
        "strike_deg": 350.0,
        "dip_deg": 20.0,
        "rake_deg": 90.0,
        "top_depth_m": 5_000.0,
        "rupture_length_m": 400_000.0,
        "rupture_width_m": 150_000.0,
        "mean_slip_m": 8.0,
        "rise_time_s": 60.0,
        "rupture_velocity_m_s": 2_500.0,
        "source": "unit-test fixture; not a physical scenario",
        "arrivals": (TsunamiArrival("hong_kong", 10_800.0, "first threshold crossing", "fixture"),),
    }
    values.update(overrides)
    return ManilaScenario(**values)


class TestManilaScenario(unittest.TestCase):
    def test_valid_scenario_binds_arrival_to_location_and_source(self) -> None:
        scenario = _scenario()
        self.assertEqual(scenario.arrivals[0].location_id, "hong_kong")
        self.assertIn("fixture", scenario.arrivals[0].source)

    def test_invalid_geometry_and_duplicate_arrival_locations_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            _scenario(dip_deg=0.0)
        duplicate = TsunamiArrival("hong_kong", 11_000.0, "maximum", "fixture")
        with self.assertRaises(ValueError):
            _scenario(arrivals=(_scenario().arrivals[0], duplicate))

    def test_manifest_refuses_unsourced_numeric_scenarios(self) -> None:
        document = json.loads((ROOT / "data/manifests/manila_scenario_sources.json").read_text())
        self.assertEqual(document["scenarios"], [])
        self.assertIn("pending", document["scenario_table_status"])
        self.assertIn("no conversion", document["required_before_scenario_registration"][-1])

    def test_manifest_retains_partial_source_families_without_promoting_them(self) -> None:
        document = json.loads((ROOT / "data/manifests/manila_scenario_sources.json").read_text())
        families = document["extracted_source_families"]
        self.assertEqual({row["segment"] for row in families}, {"north", "south"})
        self.assertEqual({row["moment_magnitude"] for row in families}, {8.1, 9.1})
        self.assertTrue(all(not row["rise_time_available"] for row in families))
        self.assertTrue(all(not row["rupture_velocity_available"] for row in families))
        self.assertEqual(document["scenarios"], [])

    def test_liu_families_keep_arrivals_location_specific_and_dynamic_fields_missing(self) -> None:
        document = json.loads((ROOT / "data/manifests/manila_scenario_sources.json").read_text())
        families = document["liu_2023_pmel_scenario_families"]
        self.assertEqual(sum(row["scenario_count"] for row in families), 19)
        self.assertEqual({row["moment_magnitude"] for row in families}, {7.5, 8.1, 8.5})
        self.assertTrue(all("macao" in row["arrival_ranges_hours"] for row in families))
        contract = document["liu_2023_extraction_contract"]
        self.assertFalse(contract["rise_time_available"])
        self.assertFalse(contract["rupture_velocity_available"])
        self.assertEqual(document["scenarios"], [])


if __name__ == "__main__":
    unittest.main()
