"""Safety gates for the selected mature elastic-load implementation."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class TestLoadGreenFunctionManifest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads(
            (ROOT / "data/manifests/load_green_function_sources.json").read_text()
        )

    def test_selected_source_is_versioned_cited_and_licensed(self) -> None:
        self.assertEqual(self.document["schema_version"], 1)
        selected = self.document["selected_candidate"]
        source = next(item for item in self.document["sources"] if item["id"] == selected)
        self.assertEqual(source["version"], "1.2.2")
        self.assertEqual(source["software_citation_doi"], "10.1029/2018EA000462")
        self.assertEqual(source["license"], "GPL-3.0")
        self.assertIn("elastic gravity load Green function", source["documented_outputs"])
        observations = source["source_audit_observations"]
        self.assertEqual(observations["observed_reference_frame_outputs"], ["CE", "CM", "CF"])
        self.assertIn("gN Newtonian response", observations["observed_gravity_outputs"])
        self.assertIn(
            "do not add LoadDef gN again".lower(), observations["project_consequence"].lower()
        )
        self.assertEqual(
            source["scientific_use_gate"]["status"],
            "ready-for-paper1-ce-provider-scope",
        )

    def test_scientific_gate_is_scoped_and_preserves_broader_failure(self) -> None:
        source = self.document["sources"][0]
        self.assertEqual(
            self.document["integration_status"],
            "validated-for-paper1-ce-provider-scope",
        )
        self.assertEqual(source["component_mapping"]["status"], "source-audited")
        self.assertEqual(len(source["local_install"]["exact_commit"]), 40)
        self.assertEqual(len(source["local_install"]["artifact_sha256"]), 64)
        gate = source["scientific_use_gate"]
        self.assertTrue(gate["source_equation_audited"])
        self.assertEqual(gate["reference_frame"], "CE")
        self.assertEqual(
            gate["published_benchmark_id"],
            "Martens2019-LoadDef-DataSets-S2-S5-provider-columns",
        )
        self.assertTrue(gate["benchmark_passed"])
        self.assertEqual(gate["strict_all_twelve_columns_status"], "failed-with-discrepancy-report")
        self.assertGreaterEqual(len(self.document["acceptance_before_scientific_use"]), 6)


if __name__ == "__main__":
    unittest.main()
