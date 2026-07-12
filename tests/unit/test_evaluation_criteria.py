"""Validate pre-registered scientific decision criteria."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load(paper: str) -> dict:
    path = ROOT / "configs" / paper / "evaluation_criteria.json"
    return json.loads(path.read_text())


class TestEvaluationCriteria(unittest.TestCase):
    def test_all_criteria_are_preregistered(self) -> None:
        for paper in ("paper1", "paper2", "paper3"):
            document = load(paper)
            self.assertEqual(document["schema_version"], 1)
            self.assertTrue(document["status"].startswith("preregistered_before_"))
            self.assertIn("primary_hypothesis", document)
            self.assertIn("decision_rule", document)

    def test_paper1_preserves_negative_results(self) -> None:
        document = load("paper1")
        self.assertEqual(document["analysis_correctness_gate"]["maximum_relative_error"], 0.01)
        self.assertEqual(len(document["atlas_convention"]["required_processes"]), 6)
        self.assertIn("non-detectable", document["decision_rule"]["negative_result"])

    def test_paper2_requires_raw_enough_data_and_holdout(self) -> None:
        document = load("paper2")
        gate = document["hard_data_gate"]
        self.assertIn("collocated_pressure", gate["required_streams"])
        self.assertGreaterEqual(gate["minimum_holdout_events"], 1)
        self.assertTrue(document["physics_closure_gate"]["forbid_atmosphere_ocean_double_counting"])
        self.assertEqual(
            document["confirmatory_metrics"]["heldout_rmse_improvement_required"],
            "strictly_positive",
        )

    def test_paper3_freezes_operational_thresholds(self) -> None:
        document = load("paper3")
        detection = document["operational_detection_gate"]
        magnitude = document["reliable_magnitude_gate"]
        self.assertGreaterEqual(detection["minimum_detection_probability"], 0.90)
        self.assertLessEqual(detection["maximum_false_alarms_per_30_day_month"], 1.0)
        self.assertEqual(magnitude["high_risk_threshold_mw"], 8.2)
        self.assertEqual(
            document["required_network_stress_tests"]["station_outage_fractions"],
            [0.0, 0.2, 0.4],
        )


if __name__ == "__main__":
    unittest.main()
