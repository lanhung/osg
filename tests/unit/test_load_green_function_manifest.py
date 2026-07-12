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

    def test_unresolved_component_mapping_forbids_scientific_use(self) -> None:
        source = self.document["sources"][0]
        self.assertNotEqual(self.document["integration_status"], "validated")
        self.assertEqual(
            source["component_mapping"]["status"],
            "requires-source-and-equation-audit",
        )
        self.assertIsNone(source["local_install"]["exact_commit"])
        self.assertGreaterEqual(len(self.document["acceptance_before_scientific_use"]), 6)


if __name__ == "__main__":
    unittest.main()
