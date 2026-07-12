"""Offline StationXML response-audit parser tests."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from fetch_fdsn_response_audit import summarize_stationxml  # noqa: E402


STATION_XML = b"""<?xml version='1.0'?>
<FDSNStationXML xmlns='http://www.fdsn.org/xml/station/1'>
  <Network code='XX'><Station code='AAA'>
    <Channel code='BHZ' locationCode='00' startDate='2024-01-01T00:00:00Z'><Response><InstrumentSensitivity/><Stage number='1'><PolesZeros/></Stage></Response></Channel>
    <Channel code='BHN' locationCode='00' startDate='2024-01-01T00:00:00Z'><Response><InstrumentSensitivity/><Stage number='1'><PolesZeros/></Stage></Response></Channel>
    <Channel code='BHE' locationCode='00' startDate='2024-01-01T00:00:00Z'><Response><InstrumentSensitivity/><Stage number='1'><PolesZeros/></Stage></Response></Channel>
    <Channel code='LHZ' locationCode='10' startDate='2024-01-01T00:00:00Z'><Response/></Channel>
    <Channel code='LH1' locationCode='10' startDate='2024-01-01T00:00:00Z'><Response/></Channel>
    <Channel code='LH2' locationCode='10' startDate='2024-01-01T00:00:00Z'><Response/></Channel>
  </Station></Network>
</FDSNStationXML>"""


class TestFdsnResponseAudit(unittest.TestCase):
    def test_triplets_preserve_epoch_and_response_completeness(self) -> None:
        result = summarize_stationxml(STATION_XML, "XX", "AAA")
        self.assertEqual(result["response_channel_count"], 6)
        self.assertEqual(result["three_component_response_epoch_count"], 2)
        by_band = {row["band"]: row for row in result["three_component_response_epochs"]}
        self.assertTrue(by_band["BH"]["response_and_sensitivity_present_for_group"])
        self.assertTrue(by_band["BH"]["full_response_structure_present_for_group"])
        self.assertFalse(by_band["LH"]["response_and_sensitivity_present_for_group"])
        self.assertFalse(by_band["LH"]["full_response_structure_present_for_group"])

    def test_wrong_station_is_empty_not_relabelled(self) -> None:
        result = summarize_stationxml(STATION_XML, "XX", "BBB")
        self.assertEqual(result["response_channel_count"], 0)
        self.assertEqual(result["three_component_response_epoch_count"], 0)


if __name__ == "__main__":
    unittest.main()
