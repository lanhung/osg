"""Paper 2 event-coverage and leakage tests."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from oceangravity.evaluation import (  # noqa: E402
    EventStationData,
    EventWindow,
    audit_event_data_gate,
    audit_event_design,
)


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


def _availability(event_id, station_id="SG1", **changes):
    values = {
        "event_id": event_id,
        "station_id": station_id,
        "gravity_product_level": "level1",
        "gravity_coverage_fraction": 0.99,
        "has_collocated_pressure": True,
        "has_calibration": True,
        "has_instrument_state": True,
        "has_sea_level_anomaly": True,
        "has_typhoon_track": True,
        "has_precipitation_and_hydrology": True,
    }
    values.update(changes)
    return EventStationData(**values)


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
            "T1",
            "typhoon",
            "training",
            "2024-01-01T00:00:00Z",
            "2024-01-03T00:00:00Z",
            ("SG1",),
            "fixture",
        )
        right = EventWindow(
            "T2",
            "typhoon",
            "held_out",
            "2024-01-02T00:00:00Z",
            "2024-01-04T00:00:00Z",
            ("SG1",),
            "fixture",
        )
        with self.assertRaisesRegex(ValueError, "overlap"):
            audit_event_design((left, right))

    def test_empty_manifest_does_not_claim_data_gate(self) -> None:
        document = json.loads((ROOT / "data/manifests/paper2_event_windows.json").read_text())
        self.assertEqual(document["events"], [])
        self.assertTrue(document["status"].startswith("pending"))

    def test_full_event_data_closure_passes_attribution_gate(self) -> None:
        windows = (
            _window("T1", "typhoon", "training", 1),
            _window("T2", "typhoon", "training", 4),
            _window("T3", "typhoon", "held_out", 7),
            _window("C1", "storm_control", "control", 10),
            _window("Q1", "quiet", "control", 13),
            _window("Q2", "quiet", "control", 16),
            _window("Q3", "quiet", "held_out", 19),
        )
        audit = audit_event_data_gate(
            windows, tuple(_availability(window.event_id) for window in windows)
        )
        self.assertTrue(audit.attribution_data_gate_passes)
        self.assertEqual(audit.eligible_pair_count, 7)
        self.assertEqual(audit.ineligible_pairs, ())
        self.assertEqual(audit.undeclared_pairs, ())

    def test_level3_or_missing_pressure_cannot_support_attribution(self) -> None:
        windows = (
            _window("T1", "typhoon", "training", 1),
            _window("T2", "typhoon", "training", 4),
            _window("T3", "typhoon", "held_out", 7),
        )
        records = (
            _availability("T1"),
            _availability("T2", gravity_product_level="level3_residual"),
            _availability("T3", has_collocated_pressure=False),
        )
        audit = audit_event_data_gate(windows, records)
        self.assertFalse(audit.attribution_data_gate_passes)
        reasons = {event: values for event, _, values in audit.ineligible_pairs}
        self.assertIn("gravity_not_raw_enough", reasons["T2"])
        self.assertIn("missing_collocated_pressure", reasons["T3"])

    def test_missing_declaration_and_invalid_availability_are_explicit(self) -> None:
        windows = (_window("T1", "typhoon", "training", 1),)
        audit = audit_event_data_gate(windows, ())
        self.assertEqual(audit.undeclared_pairs, (("T1", "SG1"),))
        self.assertFalse(audit.attribution_data_gate_passes)
        with self.assertRaises(ValueError):
            _availability("T1", gravity_coverage_fraction=1.1)
        with self.assertRaisesRegex(ValueError, "unknown event"):
            audit_event_data_gate(windows, (_availability("T2"),))


if __name__ == "__main__":
    unittest.main()
