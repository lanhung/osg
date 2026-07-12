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
        "arrivals": (
            TsunamiArrival("hong_kong", 10_800.0, "first threshold crossing", "fixture"),
        ),
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
        document = json.loads(
            (ROOT / "data/manifests/manila_scenario_sources.json").read_text()
        )
        self.assertEqual(document["scenarios"], [])
        self.assertTrue(document["scenario_table_status"].startswith("pending"))
        self.assertIn("no conversion", document["required_before_scenario_registration"][-1])


if __name__ == "__main__":
    unittest.main()
