"""Geometry and completeness tests for P1-E004."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from run_p1_distance_attenuation_foundation import run  # noqa: E402


class TestDistanceAttenuationExperiment(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        config = json.loads(
            (ROOT / "configs/paper1/distance_attenuation_foundation.json").read_text()
        )
        config["vertical_standoff_distances_m"] = [10_000.0, 100_000.0]
        cls.result = run(config)

    def test_all_processes_have_both_observables_at_each_distance(self) -> None:
        self.assertEqual(len(self.result["processes"]), 6)
        for records in self.result["processes"].values():
            self.assertEqual(len(records), 2)
            self.assertTrue(
                all(record["peak_absolute_direct_gravity_m_s2"] > 0.0 for record in records)
            )
            self.assertTrue(all(record["peak_absolute_direct_Tzz_s2"] > 0.0 for record in records))

    def test_distance_definitions_are_process_specific_and_explicit(self) -> None:
        definitions = self.result["distance_definition"]
        self.assertIn("dipole centre", definitions["internal_wave"])
        self.assertIn("source-destination midpoint", definitions["landslide"])


if __name__ == "__main__":
    unittest.main()
