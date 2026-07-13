"""Release-integrity tests for the Paper 1 v1.0 repository package."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


class TestPaper1ReleaseMetadata(unittest.TestCase):
    def test_version_citation_and_manuscript_are_aligned(self) -> None:
        pyproject = (ROOT / "pyproject.toml").read_text()
        citation = yaml.safe_load((ROOT / "CITATION.cff").read_text())
        manuscript = (ROOT / "papers/paper1_atlas/main.tex").read_text()
        self.assertIn('version = "1.0.0"', pyproject)
        self.assertEqual(citation["version"], "1.0.0")
        self.assertIn("Version 1.0 technical preprint", manuscript)
        self.assertNotIn("[PENDING:", manuscript)

    def test_ai_review_disclosure_cannot_be_mistaken_for_human_review(self) -> None:
        review = json.loads((ROOT / "data/manifests/paper1_human_review.json").read_text())
        self.assertEqual(review["reviewer"]["type"], "AI system")
        self.assertTrue(review["reviewer"]["prior_implementation_involvement"])
        self.assertTrue(review["human_review_still_recommended_before_journal_submission"])

    def test_review_correction_is_registered_and_robust(self) -> None:
        metrics = json.loads(
            (
                ROOT / "experiments/paper1/P1-E010-independent-review-sensitivity/metrics.json"
            ).read_text()
        )
        self.assertEqual(metrics["record_count"], 1446)
        self.assertTrue(metrics["all_robustness_checks_pass"])
        self.assertTrue(all(metrics["registered_e008_median_requirements_reproduced"].values()))
        self.assertEqual(metrics["reviewed_instrument_lowest_edge_hz"], 5.0e-4)

    def test_licenses_and_deposition_metadata_exist(self) -> None:
        self.assertIn("MIT License", (ROOT / "LICENSE").read_text())
        self.assertIn("Creative Commons", (ROOT / "LICENSES.md").read_text())
        deposition = json.loads((ROOT / ".zenodo.json").read_text())
        self.assertEqual(deposition["version"], "1.0.0")
        self.assertNotIn("doi", deposition)


if __name__ == "__main__":
    unittest.main()
