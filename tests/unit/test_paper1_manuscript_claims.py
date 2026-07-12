"""Claim and pending-gate checks for the Paper 1 manuscript source."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class TestPaper1ManuscriptClaims(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manuscript = (ROOT / "papers/paper1_atlas/main.tex").read_text()

    def test_working_title_and_locked_increment_are_present(self) -> None:
        self.assertIn(
            "Frequency-Coverage Limits in Assessing Gravity Signals "
            "from Oceanic Mass Redistribution",
            self.manuscript,
        )
        self.assertIn("cross-process, cross-distance, cross-instrument", self.manuscript)
        self.assertIn("direct radial gravity", self.manuscript)
        self.assertIn("not counts of independent natural events", self.manuscript)

    def test_forbidden_claims_are_absent(self) -> None:
        lowered = self.manuscript.lower()
        self.assertNotIn("first environmental newtonian-noise model", lowered)
        self.assertNotIn("first instrument-noise calculation", lowered)

    def test_registered_results_and_figure_statuses_are_explicit(self) -> None:
        self.assertIn("1,446", self.manuscript)
        self.assertIn("15.6", self.manuscript)
        self.assertIn("We therefore withhold", self.manuscript)
        self.assertIn("SNR classifications rather than extrapolating", self.manuscript)
        figures = json.loads((ROOT / "papers/paper1_atlas/figure_manifest.json").read_text())
        self.assertEqual(len(figures["figures"]), 4)
        self.assertEqual(figures["registered_input"], "P1-E006-evidence-bounded-atlas")
        self.assertEqual([item["status"] for item in figures["figures"]].count("complete"), 2)


if __name__ == "__main__":
    unittest.main()
