"""Paper 2 event-coverage and leakage tests."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from oceangravity.evaluation import EventWindow, audit_event_design  # noqa: E402


def _window(identifier, event_type, role, start_day, stations=("SG1",)):
    return EventWindow(
        event_id=identifier,
        event_type=event_type,
        split_role=role,
        start_utc=f"2024-01-{start_day:02d}T00:00:00Z",
        end_utc=f"2024-01-{start_day + 1:02d}T00:00:00Z",
        station_ids=stations,
        source="unit-test fixture",
    )


class TestEventDesign(unittest.TestCase):
    def test_one_station_three_typhoons_passes_raw_gate(self) -> None:
        windows = (
            _window("T1", "typhoon", "training", 1),
            _window("T2", "typhoon", "training", 4),
            _window("T3", "typhoon", "held_out", 7),
            _window("C1", "storm_control", "control", 10),
            _window("Q1", "quiet", "control", 13),
            _window("Q2", "quiet", "control", 16),
            _window("Q3", "quiet", "held_out", 19),
        )
        audit = audit_event_design(windows)
        self.assertTrue(audit.raw_data_gate_passes)
        self.assertTrue(audit.evaluation_design_ready)
        self.assertEqual(audit.typhoon_counts_by_station, (("SG1", 3),))

    def test_two_stations_two_typhoons_each_passes_alternative(self) -> None:
        windows = (
            _window("T1", "typhoon", "training", 1, ("SG1", "SG2")),
            _window("T2", "typhoon", "held_out", 4, ("SG1", "SG2")),
        )
        audit = audit_event_design(windows)
        self.assertTrue(audit.raw_data_gate_passes)
        self.assertFalse(audit.evaluation_design_ready)

    def test_same_station_overlap_across_events_is_rejected(self) -> None:
        left = EventWindow(
            "T1", "typhoon", "training", "2024-01-01T00:00:00Z",
            "2024-01-03T00:00:00Z", ("SG1",), "fixture"
        )
        right = EventWindow(
            "T2", "typhoon", "held_out", "2024-01-02T00:00:00Z",
            "2024-01-04T00:00:00Z", ("SG1",), "fixture"
        )
        with self.assertRaisesRegex(ValueError, "overlap"):
            audit_event_design((left, right))

    def test_empty_manifest_does_not_claim_data_gate(self) -> None:
        document = json.loads(
            (ROOT / "data/manifests/paper2_event_windows.json").read_text()
        )
        self.assertEqual(document["events"], [])
        self.assertTrue(document["status"].startswith("pending"))


if __name__ == "__main__":
    unittest.main()
