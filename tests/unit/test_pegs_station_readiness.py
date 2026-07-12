"""Station epoch readiness tests for Paper 3."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.pegs import (  # noqa: E402
    StationEpochReadiness,
    audit_station_readiness,
)


def _epoch(identifier, station, **changes):
    values = {
        "epoch_id": identifier,
        "network": "XX",
        "station": station,
        "location": "00",
        "channels": ("BHZ", "BHN", "BHE"),
        "response_status": "verified_full",
        "waveform_status": "downloadable",
        "license_status": "permitted",
        "latency_class": "near_real_time",
        "noise_qc_complete": True,
    }
    values.update(changes)
    return StationEpochReadiness(**values)


class TestPegsStationReadiness(unittest.TestCase):
    def test_ready_archive_and_operational_epochs_are_distinguished(self) -> None:
        live = _epoch("live", "AAA")
        archive = _epoch("archive", "BBB", latency_class="archive_only")
        audit = audit_station_readiness(
            (archive, live), minimum_operational_station_count=1
        )
        self.assertEqual(audit.retrospective_station_count, 2)
        self.assertEqual(audit.operational_station_count, 1)
        self.assertEqual(audit.operational_ready_epoch_ids, ("live",))
        self.assertTrue(audit.inventory_smoke_gate_passes)

    def test_response_waveform_license_and_noise_failures_are_explicit(self) -> None:
        rows = (
            _epoch("response", "A", response_status="partial"),
            _epoch("waveform", "B", waveform_status="restricted"),
            _epoch("license", "C", license_status="unknown"),
            _epoch("noise", "D", noise_qc_complete=False),
            _epoch("triplet", "E", channels=("BHZ", "BHN")),
        )
        audit = audit_station_readiness(rows, minimum_operational_station_count=1)
        self.assertFalse(audit.inventory_smoke_gate_passes)
        reasons = dict(audit.ineligible_epochs)
        self.assertIn("full_response_not_verified", reasons["response"])
        self.assertIn("waveform_not_downloadable", reasons["waveform"])
        self.assertIn("license_not_permitted", reasons["license"])
        self.assertIn("noise_qc_incomplete", reasons["noise"])
        self.assertIn("missing_three_component_triplet", reasons["triplet"])

    def test_one_two_horizontal_codes_are_accepted(self) -> None:
        epoch = _epoch("numeric", "AAA", channels=("LHZ", "LH1", "LH2"))
        self.assertTrue(epoch.has_three_component_triplet)

    def test_invalid_and_duplicate_epochs_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            _epoch("mixed", "AAA", channels=("BHZ", "BHN", "LHE"))
        row = _epoch("same", "AAA")
        with self.assertRaises(ValueError):
            audit_station_readiness((row, row), minimum_operational_station_count=1)
        with self.assertRaises(ValueError):
            audit_station_readiness((), minimum_operational_station_count=0)
