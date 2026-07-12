"""Offline FDSN archive-extent audit tests."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from fetch_fdsn_availability_audit import summarize_availability  # noqa: E402


class TestFdsnAvailabilityAudit(unittest.TestCase):
    def test_triplet_uses_common_overlap_and_preserves_gap_count(self) -> None:
        rows = []
        for component, earliest, latest, spans in (
            ("Z", "2024-01-01T00:00:00Z", "2024-12-31T00:00:00Z", 3),
            ("1", "2024-02-01T00:00:00Z", "2024-12-30T00:00:00Z", 5),
            ("2", "2024-01-15T00:00:00Z", "2024-12-29T00:00:00Z", 4),
        ):
            rows.append(
                {
                    "network": "XX",
                    "station": "AAA",
                    "location": "00",
                    "channel": "BH" + component,
                    "quality": "M",
                    "samplerate": 20.0,
                    "earliest": earliest,
                    "latest": latest,
                    "timespanCount": spans,
                    "restriction": "OPEN",
                }
            )
        result = summarize_availability({"datasources": rows}, "XX", "AAA")
        self.assertEqual(result["three_component_archive_extent_count"], 1)
        triplet = result["three_component_archive_extents"][0]
        self.assertEqual(triplet["common_earliest"], "2024-02-01T00:00:00+00:00")
        self.assertEqual(triplet["common_latest"], "2024-12-29T00:00:00+00:00")
        self.assertEqual(triplet["maximum_timespan_count"], 5)
        self.assertTrue(triplet["all_open"])

    def test_wrong_identity_does_not_relabel_archive_rows(self) -> None:
        result = summarize_availability({"datasources": []}, "XX", "AAA")
        self.assertEqual(result["archive_channel_extent_count"], 0)
        self.assertEqual(result["three_component_archive_extent_count"], 0)


if __name__ == "__main__":
    unittest.main()
