"""Paper 2 manifest-to-decision adapter tests."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "audit_paper2_data_gate", ROOT / "scripts/audit_paper2_data_gate.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def _event(identifier, event_type, role, day):
    return {
        "event_id": identifier,
        "event_type": event_type,
        "split_role": role,
        "start_utc": f"2024-02-{day:02d}T00:00:00Z",
        "end_utc": f"2024-02-{day + 1:02d}T00:00:00Z",
        "station_ids": ["SG1"],
        "source": "unit-test fixture",
    }


def _data(identifier):
    return {
        "event_id": identifier,
        "station_id": "SG1",
        "gravity_product_level": "level1",
        "gravity_coverage_fraction": 0.99,
        "has_collocated_pressure": True,
        "has_calibration": True,
        "has_instrument_state": True,
        "has_sea_level_anomaly": True,
        "has_typhoon_track": True,
        "has_precipitation_and_hydrology": True,
    }


class TestPaper2DataGateCli(unittest.TestCase):
    def test_repository_manifest_truthfully_remains_pending(self) -> None:
        document = json.loads((ROOT / "data/manifests/paper2_event_windows.json").read_text())
        result = MODULE.audit_manifest(document)
        self.assertEqual(result["decision"], "pending_no_event_windows")
        self.assertFalse(result["attribution_data_gate_passes"])

    def test_frozen_complete_manifest_produces_go_decision(self) -> None:
        specifications = (
            ("T1", "typhoon", "training", 1),
            ("T2", "typhoon", "training", 4),
            ("T3", "typhoon", "held_out", 7),
            ("C1", "storm_control", "control", 10),
            ("Q1", "quiet", "control", 13),
            ("Q2", "quiet", "control", 16),
            ("Q3", "quiet", "held_out", 19),
        )
        document = {
            "schema_version": 1,
            "decision_status": "frozen",
            "minimum_gravity_coverage_fraction": 0.95,
            "events": [_event(*row) for row in specifications],
            "station_data_availability": [_data(row[0]) for row in specifications],
        }
        result = MODULE.audit_manifest(document)
        self.assertEqual(result["decision"], "go_full_attribution")
        self.assertTrue(result["attribution_data_gate_passes"])

    def test_draft_incomplete_manifest_cannot_emit_final_go(self) -> None:
        document = {
            "schema_version": 1,
            "decision_status": "draft",
            "minimum_gravity_coverage_fraction": 0.95,
            "events": [_event("T1", "typhoon", "training", 1)],
            "station_data_availability": [],
        }
        result = MODULE.audit_manifest(document)
        self.assertEqual(result["decision"], "draft_no_go")
        self.assertFalse(result["attribution_data_gate_passes"])


if __name__ == "__main__":
    unittest.main()
