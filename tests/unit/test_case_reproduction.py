"""Published scalar case-target evaluation tests."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from oceangravity.evaluation import CaseTarget, evaluate_case_reproduction  # noqa: E402


class TestCaseReproduction(unittest.TestCase):
    def test_fractional_and_absolute_targets(self) -> None:
        targets = (
            CaseTarget("amplitude", 10.0, "m/s2", "fractional", 0.2, "fixture"),
            CaseTarget("correlation", 0.87, "1", "absolute", 0.05, "fixture"),
        )
        passed = evaluate_case_reproduction(
            "case", targets, {"amplitude": 8.0, "correlation": 0.83}
        )
        self.assertEqual(passed.status, "pass")
        failed = evaluate_case_reproduction(
            "case", targets, {"amplitude": 7.9, "correlation": 0.83}
        )
        self.assertEqual(failed.status, "fail")

    def test_missing_target_remains_pending_and_failure_takes_precedence(self) -> None:
        targets = (
            CaseTarget("a", 1.0, "1", "absolute", 0.1, "fixture"),
            CaseTarget("b", 2.0, "1", "absolute", 0.1, "fixture"),
        )
        pending = evaluate_case_reproduction("case", targets, {"a": 1.0})
        self.assertEqual(pending.status, "pending")
        failed = evaluate_case_reproduction("case", targets, {"a": 2.0})
        self.assertEqual(failed.status, "fail")

    def test_helgoland_targets_preserve_exact_paper_values(self) -> None:
        config = json.loads(
            (ROOT / "configs/paper1/helgoland_reproduction.json").read_text()
        )
        targets = {row["target_id"]: row for row in config["targets"]}
        self.assertEqual(config["event"]["peak_time_utc"], "2022-01-30T05:00:00Z")
        self.assertEqual(targets["event_gravity_peak_to_peak_m_s2"]["expected_value"], 8.5e-8)
        self.assertEqual(targets["event_vertical_displacement_m"]["expected_value"], -0.034)
        self.assertEqual(targets["month_bsh_gravity_correlation"]["expected_value"], 0.87)
        self.assertEqual(
            targets["month_bsh_gravity_rms_reduction_fraction"]["expected_value"],
            0.49,
        )
        self.assertIn("not outreach-page", config["rounding_policy"])

    def test_invalid_targets_and_unknown_observations_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            CaseTarget("zero", 0.0, "1", "fractional", 0.1, "fixture")
        target = CaseTarget("known", 1.0, "1", "absolute", 0.1, "fixture")
        with self.assertRaisesRegex(ValueError, "undeclared"):
            evaluate_case_reproduction("case", (target,), {"unknown": 1.0})


if __name__ == "__main__":
    unittest.main()
