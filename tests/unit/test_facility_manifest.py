"""Ensure facility-level capabilities are not silently treated as noise curves."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


class TestFacilityManifest(unittest.TestCase):
    def test_hust_record_is_traceable_and_not_noise_curve_eligible(self) -> None:
        root = Path(__file__).resolve().parents[2]
        document = json.loads(
            (root / "data/manifests/facility_capabilities.json").read_text()
        )
        self.assertEqual(document["schema_version"], 1)
        self.assertEqual(len(document["facilities"]), 1)
        facility = document["facilities"][0]
        self.assertEqual(
            facility["facility_id"],
            "hust_national_precise_gravity_measurement_facility",
        )
        self.assertFalse(facility["noise_curve_eligible"])
        self.assertTrue(any("ASD" in limitation for limitation in facility["limitations"]))
        self.assertTrue(facility["source"].startswith("https://kjt.hubei.gov.cn/"))


if __name__ == "__main__":
    unittest.main()

