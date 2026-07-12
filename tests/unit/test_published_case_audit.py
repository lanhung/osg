"""Unified published-case gate tests."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "audit_published_cases", ROOT / "scripts/audit_published_cases.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class TestPublishedCaseAudit(unittest.TestCase):
    def test_both_required_cases_are_present_and_pending(self) -> None:
        result = MODULE.audit_all_cases()
        self.assertEqual(
            {case["case_id"] for case in result["cases"]},
            {
                "helgoland-ntol-2022-voigt-2024",
                "haikou-ntol-2023-2024-zhang-2026",
            },
        )
        self.assertEqual(result["status_counts"], {"pass": 0, "fail": 0, "pending": 2})
        self.assertFalse(result["all_required_cases_pass"])


if __name__ == "__main__":
    unittest.main()
