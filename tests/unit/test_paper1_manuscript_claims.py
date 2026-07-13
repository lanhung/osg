"""Claim and pending-gate checks for the Paper 1 manuscript source."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


class TestPaper1ManuscriptClaims(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manuscript = (ROOT / "papers/paper1_atlas/main.tex").read_text()
        cls.claims = yaml.safe_load((ROOT / "claims.yml").read_text())["paper1"]
        cls.roadmap = (ROOT / "docs/roadmap.md").read_text()

    def test_working_title_and_locked_increment_are_present(self) -> None:
        self.assertIn(
            "Frequency-Coverage Limits in Assessing Gravity Signals "
            "from Oceanic Mass Redistribution",
            self.manuscript,
        )
        self.assertIn("cross-process direct-", self.manuscript)
        self.assertIn("direct radial gravity", self.manuscript)
        self.assertIn("not counts of independent natural events", self.manuscript)
        self.assertIn("Observable and evidence framework", self.manuscript)
        self.assertIn("Supplementary Figure~S1", self.manuscript)
        self.assertIn("Direct-radial-gravity frequency requirements", self.manuscript)

    def test_forbidden_claims_are_absent(self) -> None:
        lowered = self.manuscript.lower()
        self.assertNotIn("first environmental newtonian-noise model", lowered)
        self.assertNotIn("first instrument-noise calculation", lowered)

    def test_route_a_governance_is_aligned(self) -> None:
        self.assertEqual(
            self.claims["working_title"],
            "Frequency-Coverage Limits in Assessing Gravity Signals from Oceanic "
            "Mass Redistribution",
        )
        self.assertIn("direct radial gravity", self.claims["claim"])
        self.assertIn(
            "a completed decision-grade detectability atlas",
            self.claims["forbidden_claims"],
        )
        self.assertIn("Cancel the distance--SNR panel for Route A", self.roadmap)
        self.assertIn(
            "Move gravity-gradient detectability to the supplement/future-work boundary",
            self.roadmap,
        )

    def test_registered_results_and_figure_statuses_are_explicit(self) -> None:
        self.assertIn("1,446", self.manuscript)
        self.assertIn("15.6", self.manuscript)
        self.assertIn("We therefore withhold", self.manuscript)
        self.assertIn("SNR classifications rather than extrapolating", self.manuscript)
        figures = json.loads((ROOT / "papers/paper1_atlas/figure_manifest.json").read_text())
        self.assertEqual(len(figures["figures"]), 5)
        self.assertEqual(
            figures["registered_inputs"],
            [
                "P1-E006-evidence-bounded-atlas",
                "P1-E008-frequency-coverage-requirements",
                "P1-E009-helgoland-component-audit",
            ],
        )
        self.assertEqual([item["status"] for item in figures["figures"]].count("complete"), 5)

    def test_release_gate_snapshot_does_not_claim_submission_readiness(self) -> None:
        release = json.loads((ROOT / "configs/paper1/release_gates.json").read_text())
        gates = {row["id"]: row["status"] for row in release["gates"]}
        self.assertEqual(set(gates), {f"G{index}" for index in range(1, 11)})
        self.assertTrue(all(gates[f"G{index}"] == "pass" for index in range(1, 8)))
        self.assertEqual(gates["G8"], "pending")
        self.assertEqual(gates["G9"], "pass")
        self.assertEqual(gates["G10"], "pending")
        self.assertFalse(release["release_candidate_ready"])


if __name__ == "__main__":
    unittest.main()
