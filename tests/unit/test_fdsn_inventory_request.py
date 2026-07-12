"""Offline tests for the versioned EarthScope station inventory request."""

from __future__ import annotations

import argparse
import sys
import unittest
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from fetch_fdsn_station_inventory import ENDPOINT, build_url  # noqa: E402


class TestFdsnInventoryRequest(unittest.TestCase):
    def test_url_uses_current_endpoint_and_frozen_parameters(self) -> None:
        args = argparse.Namespace(
            minlatitude=5.0,
            maxlatitude=30.0,
            minlongitude=100.0,
            maxlongitude=130.0,
            channel="BH?,LH?",
            starttime="2020-01-01T00:00:00",
            endtime="2026-07-12T00:00:00",
        )
        url = build_url(args)
        self.assertTrue(url.startswith(ENDPOINT + "?"))
        query = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
        self.assertEqual(query["level"], ["channel"])
        self.assertEqual(query["format"], ["text"])
        self.assertEqual(query["channel"], ["BH?,LH?"])
        self.assertEqual(query["includerestricted"], ["false"])
        self.assertNotIn("includeavailability", query)
        self.assertNotIn("matchtimeseries", query)


if __name__ == "__main__":
    unittest.main()

