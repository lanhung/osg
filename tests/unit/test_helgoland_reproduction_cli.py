"""Helgoland manifest-to-audit adapter tests."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "evaluate_helgoland_reproduction",
    ROOT / "scripts/evaluate_helgoland_reproduction.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class TestHelgolandReproductionCli(unittest.TestCase):
    def setUp(self) -> None:
        self.configuration = json.loads(
            (ROOT / "configs/paper1/helgoland_reproduction.json").read_text()
        )
        self.inputs = json.loads(
            (ROOT / "data/manifests/helgoland_reproduction_inputs.json").read_text()
        )

    def test_repository_case_truthfully_remains_pending(self) -> None:
        result = MODULE.evaluate_documents(self.configuration, self.inputs)
        self.assertEqual(result["status"], "pending")
        self.assertTrue(all(row["status"] == "pending" for row in result["targets"]))

    def test_exact_frozen_values_pass_adapter(self) -> None:
        inputs = dict(self.inputs)
        inputs["observed_reproduction_values"] = {
            row["target_id"]: row["expected_value"] for row in self.configuration["targets"]
        }
        result = MODULE.evaluate_documents(self.configuration, inputs)
        self.assertEqual(result["status"], "pass")

    def test_case_id_mismatch_is_rejected(self) -> None:
        inputs = dict(self.inputs, case_id="different")
        with self.assertRaisesRegex(ValueError, "case IDs"):
            MODULE.evaluate_documents(self.configuration, inputs)


if __name__ == "__main__":
    unittest.main()
