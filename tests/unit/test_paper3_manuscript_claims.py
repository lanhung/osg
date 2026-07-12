"""Claim and operational-metric tests for the Paper 3 manuscript."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class TestPaper3ManuscriptClaims(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = (ROOT / "papers/paper3_pegs/main.tex").read_text()
        cls.lowered = cls.text.lower()

    def test_regional_operational_increment_is_present(self) -> None:
        for phrase in (
            "South China and surrounding networks",
            "false alarms per 30-day month",
            "reliable magnitude time",
            "20\\%, and 40\\% outage",
            "conditional GNN",
        ):
            self.assertIn(phrase.lower(), self.lowered)

    def test_forbidden_claims_are_absent(self) -> None:
        for forbidden in (
            "first pegs tsunami-warning proposal",
            "first manila trench tsunami simulation",
            "first real-time pegs monitoring-system implementation",
            "first empirical-noise",
        ):
            self.assertNotIn(forbidden, self.lowered)

    def test_all_seven_figures_remain_pending(self) -> None:
        document = json.loads(
            (ROOT / "papers/paper3_pegs/figure_manifest.json").read_text()
        )
        self.assertEqual(len(document["figures"]), 7)
        self.assertTrue(all(item["status"].startswith("pending") for item in document["figures"]))


if __name__ == "__main__":
    unittest.main()
