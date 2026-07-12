"""Haikou VOR target and executable pending-state tests."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "evaluate_haikou_reproduction", ROOT / "scripts/evaluate_haikou_reproduction.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class TestHaikouReproduction(unittest.TestCase):
    def setUp(self) -> None:
        self.configuration = json.loads(
            (ROOT / "configs/paper1/haikou_reproduction.json").read_text()
        )
        self.inputs = json.loads(
            (ROOT / "data/manifests/haikou_reproduction_inputs.json").read_text()
        )

    def test_vor_values_and_typhoon_scope_are_frozen(self) -> None:
        targets = {row["target_id"]: row for row in self.configuration["targets"]}
        self.assertEqual(targets["cmems_ntol_maximum_variation_m_s2"]["expected_value"], 2.6e-8)
        self.assertEqual(targets["cmems_sg_residual_correlation"]["expected_value"], 0.83)
        self.assertEqual(targets["cmems_mpiom_correlation"]["expected_value"], 0.87)
        self.assertEqual(
            targets["cmems_corrected_sg_residual_rms_m_s2"]["expected_value"],
            5.0e-9,
        )
        self.assertEqual(self.configuration["typhoon_scope"]["named_typhoon_events_analyzed"], 0)
        self.assertFalse(self.configuration["typhoon_scope"]["event_windows_present"])

    def test_current_reproduction_is_pending_not_failed_or_passed(self) -> None:
        result = MODULE.evaluate_documents(self.configuration, self.inputs)
        self.assertEqual(result["status"], "pending")
        self.assertFalse(result["typhoon_event_attribution_eligible"])
        self.assertTrue(all(row["status"] == "pending" for row in result["targets"]))

    def test_exact_values_pass_adapter_but_do_not_change_typhoon_scope(self) -> None:
        inputs = dict(self.inputs)
        inputs["observed_reproduction_values"] = {
            row["target_id"]: row["expected_value"] for row in self.configuration["targets"]
        }
        result = MODULE.evaluate_documents(self.configuration, inputs)
        self.assertEqual(result["status"], "pass")
        self.assertFalse(result["typhoon_event_attribution_eligible"])

    def test_observation_inputs_remain_restricted(self) -> None:
        inputs = {row["id"]: row for row in self.inputs["inputs"]}
        self.assertIn("not public", inputs["igrav048-gravity-pressure-state"]["availability"])
        self.assertIsNone(inputs["igrav048-gravity-pressure-state"]["sha256"])


if __name__ == "__main__":
    unittest.main()
