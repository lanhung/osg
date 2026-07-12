"""Offline channel-triplet tests for the Paper 3 station inventory."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from summarize_fdsn_inventory import summarize_inventory  # noqa: E402

HEADER = (
    "#Network|Station|Location|Channel|Latitude|Longitude|Elevation|Depth|"
    "Azimuth|Dip|SensorDescription|Scale|ScaleFreq|ScaleUnits|SampleRate|"
    "StartTime|EndTime"
)


def _row(
    channel: str,
    *,
    station: str = "AAA",
    scale: str = "1.0",
    end_time: str = "2025-01-01T00:00:00",
) -> str:
    return (
        f"XX|{station}|00|{channel}|20.0|120.0|10|0|0|-90|sensor|{scale}|1|"
        f"M/S|20|2024-01-01T00:00:00|{end_time}"
    )


class TestFdsnInventorySummary(unittest.TestCase):
    def test_triplets_are_kept_and_incomplete_epochs_are_separate(self) -> None:
        payload = (
            "\n".join(
                (
                    HEADER,
                    _row("BHZ"),
                    _row("BHN"),
                    _row("BHE"),
                    _row("LHZ", station="BBB"),
                    _row("LH1", station="BBB"),
                    _row("LH2", station="BBB"),
                    _row("BHZ", station="CCC"),
                    _row("HHZ", station="DDD"),
                )
            )
            + "\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "inventory.txt"
            path.write_text(payload, encoding="utf-8")
            result = summarize_inventory(path)
        self.assertEqual(result["candidate_epoch_count"], 2)
        self.assertEqual(result["incomplete_epoch_count"], 1)
        stations = {item["station"] for item in result["three_component_candidates"]}
        self.assertEqual(stations, {"AAA", "BBB"})
        self.assertTrue(
            all(not item["full_response_verified"] for item in result["three_component_candidates"])
        )
        self.assertIn("do not establish", result["warning"])
        self.assertEqual(result["open_ended_candidate_epoch_count"], 0)

    def test_scalar_sensitivity_missing_is_recorded_not_promoted(self) -> None:
        payload = "\n".join((HEADER, _row("BHZ", scale=""), _row("BHN"), _row("BHE"))) + "\n"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "inventory.txt"
            path.write_text(payload, encoding="utf-8")
            result = summarize_inventory(path)
        candidate = result["three_component_candidates"][0]
        self.assertFalse(candidate["scalar_sensitivity_present_for_all_channels"])
        self.assertFalse(candidate["full_response_verified"])

    def test_open_ended_epochs_are_counted_without_claiming_operation(self) -> None:
        payload = (
            "\n".join(
                (
                    HEADER,
                    _row("BHZ", end_time=""),
                    _row("BHN", end_time=""),
                    _row("BHE", end_time=""),
                )
            )
            + "\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "inventory.txt"
            path.write_text(payload, encoding="utf-8")
            result = summarize_inventory(path)
        self.assertEqual(result["open_ended_candidate_epoch_count"], 1)
        self.assertEqual(result["open_ended_unique_network_station_count"], 1)
        self.assertEqual(result["open_ended_networks"], ["XX"])
        self.assertIn("does not establish current operation", result["warning"])


if __name__ == "__main__":
    unittest.main()
