"""Claim-safety tests for process parameter evidence anchors."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class TestProcessParameterEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads(
            (ROOT / "data/manifests/process_parameter_evidence.json").read_text()
        )

    def test_all_six_processes_are_present(self) -> None:
        self.assertEqual(
            set(self.document["processes"]),
            {
                "tide",
                "storm_surge",
                "mesoscale_eddy",
                "internal_wave",
                "tsunami",
                "submarine_landslide",
            },
        )

    def test_examples_and_means_are_not_probability_priors(self) -> None:
        evidence = [
            item
            for process in self.document["processes"].values()
            for item in process["evidence"]
        ]
        self.assertGreater(len(evidence), 0)
        self.assertTrue(all(not item["probability_prior_eligible"] for item in evidence))

    def test_unresolved_processes_cannot_enter_scientific_ensemble(self) -> None:
        for name in ("internal_wave", "tsunami", "submarine_landslide"):
            process = self.document["processes"][name]
            self.assertEqual(process["evidence"], [])
            self.assertGreaterEqual(len(process["unresolved_for_atlas"]), 3)


if __name__ == "__main__":
    unittest.main()
