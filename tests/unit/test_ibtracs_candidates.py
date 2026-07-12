"""Offline tests for versioned IBTrACS retrieval and regional selection."""

from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from select_ibtracs_candidates import select_candidates  # noqa: E402


class TestIbtracsCandidates(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = json.loads(
            (ROOT / "configs/paper2/ibtracs_south_china_sea.json").read_text()
        )

    def test_manifest_freezes_release_url_doi_and_retrieved_checksum(self) -> None:
        manifest = json.loads((ROOT / "data/manifests/paper2_ibtracs.json").read_text())
        self.assertEqual(manifest["release"], "v04r01")
        self.assertIn("ncei.noaa.gov", manifest["download_url"])
        self.assertEqual(manifest["dataset_doi"], "10.25921/82ty-9e16")
        retrieval = manifest["retrieval"]
        self.assertRegex(retrieval["sha256"], re.compile(r"^[0-9a-f]{64}$"))
        self.assertGreater(retrieval["size_bytes"], 0)
        candidates = json.loads(
            (
                ROOT
                / "data/manifests/paper2_ibtracs_candidates_2026-07-12.json"
            ).read_text()
        )
        self.assertEqual(candidates["input_sha256"], retrieval["sha256"])
        self.assertGreater(candidates["candidate_count"], 0)
        self.assertIn("SHA-256", manifest["update_warning"])

    def test_selection_keeps_agency_intensity_fields_separate(self) -> None:
        payload = "\n".join(
            (
                "SID,SEASON,BASIN,NAME,ISO_TIME,LAT,LON,WMO_WIND,WMO_PRES,USA_WIND,USA_PRES",
                ",Year,Basin,Name,UTC,degrees_north,degrees_east,kt,mb,kt,mb",
                "2024001N10120,2024,WP,ALPHA,2024-07-01 00:00:00,10,120,40,990,45,985",
                "2024001N10120,2024,WP,ALPHA,2024-07-01 06:00:00,12,122,50,980,55,975",
                "2024001N10120,2024,WP,ALPHA,2024-07-01 12:00:00,30,130,80,950,85,945",
                "2024002N10120,2024,EP,BETA,2024-07-02 00:00:00,10,120,60,970,65,965",
            )
        ) + "\n"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ibtracs.csv"
            path.write_text(payload, encoding="utf-8")
            result = select_candidates(path, self.config)
        self.assertEqual(result["candidate_count"], 1)
        event = result["events"][0]
        self.assertEqual(event["regional_track_points"], 2)
        self.assertEqual(event["maximum_wmo_wind_kt"], 50.0)
        self.assertEqual(event["minimum_wmo_pressure_mb"], 980.0)
        self.assertEqual(event["maximum_usa_wind_kt"], 55.0)
        self.assertEqual(event["minimum_usa_pressure_mb"], 975.0)
        self.assertGreater(event["closest_reference_distance_km"], 0.0)
        self.assertFalse(event["shortlist_screening_passes"])
        self.assertIn(
            "closest_reference_distance_exceeds_limit",
            event["shortlist_screening_failures"],
        )
        self.assertIn("does not imply", result["warning"])


if __name__ == "__main__":
    unittest.main()
