"""Production process-prior gate tests."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "audit_process_prior_readiness",
    ROOT / "scripts/audit_process_prior_readiness.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class TestProcessPriorReadiness(unittest.TestCase):
    def test_repository_correctly_blocks_all_production_processes(self) -> None:
        document = json.loads(
            (ROOT / "data/manifests/process_parameter_evidence.json").read_text()
        )
        result = MODULE.audit_document(document)
        self.assertEqual(result["process_count"], 6)
        self.assertEqual(result["ready_count"], 0)
        self.assertFalse(result["all_processes_ready"])
        self.assertTrue(
            all(
                "missing_frozen_production_joint_design" in row["blockers"]
                for row in result["processes"]
            )
        )

    def test_complete_sensitivity_design_can_pass_without_probability_claim(self) -> None:
        document = {
            "schema_version": 1,
            "processes": {
                "fixture": {
                    "evidence": [{"source": "fixture"}],
                    "unresolved_for_atlas": [],
                    "production_joint_design": {
                        "status": "frozen",
                        "semantics": "sensitivity_design_not_probability",
                        "parameters": {"amplitude": {"range": [1.0, 2.0]}},
                    },
                }
            },
        }
        result = MODULE.audit_document(document)
        self.assertTrue(result["all_processes_ready"])

    def test_unresolved_fields_override_a_frozen_design(self) -> None:
        document = {
            "schema_version": 1,
            "processes": {
                "fixture": {
                    "evidence": [{"source": "fixture"}],
                    "unresolved_for_atlas": ["density"],
                    "production_joint_design": {
                        "status": "frozen",
                        "semantics": "probability_prior",
                        "parameters": {"amplitude": {"range": [1.0, 2.0]}},
                    },
                }
            },
        }
        result = MODULE.audit_document(document)
        self.assertFalse(result["all_processes_ready"])
        self.assertIn(
            "unresolved_physics_or_parameter_fields",
            result["processes"][0]["blockers"],
        )


if __name__ == "__main__":
    unittest.main()
