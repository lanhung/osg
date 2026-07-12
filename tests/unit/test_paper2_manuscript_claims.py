"""Claim and data-gate tests for the Paper 2 manuscript."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class TestPaper2ManuscriptClaims(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = (ROOT / "papers/paper2_typhoon/main.tex").read_text()

    def test_title_increment_and_holdout_are_present(self) -> None:
        self.assertIn("Event-Resolved Gravimetric Detection", self.text)
        self.assertIn("named-typhoon attribution", self.text)
        self.assertIn("held-out typhoon", self.text)
        self.assertIn("Double-count audit", self.text)

    def test_forbidden_novelty_claims_are_absent(self) -> None:
        lowered = self.text.lower()
        for forbidden in (
            "first south china sea non-tidal ocean-loading study",
            "first typhoon gravimetry study",
            "first typhoon-event extraction",
            "first cmems-versus-mpiom comparison",
        ):
            self.assertNotIn(forbidden, lowered)

    def test_all_six_figures_remain_pending(self) -> None:
        document = json.loads(
            (ROOT / "papers/paper2_typhoon/figure_manifest.json").read_text()
        )
        self.assertEqual(len(document["figures"]), 6)
        self.assertTrue(all(item["status"].startswith("pending") for item in document["figures"]))


if __name__ == "__main__":
    unittest.main()
