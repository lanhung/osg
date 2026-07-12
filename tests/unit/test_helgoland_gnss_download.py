"""Helgoland GNSS download-plan tests."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "download_helgoland_gnss_rinex",
    ROOT / "scripts/download_helgoland_gnss_rinex.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class TestHelgolandGnssDownload(unittest.TestCase):
    def test_registered_plan_has_both_stations_and_full_window(self) -> None:
        manifest = json.loads(
            (ROOT / "data/manifests/helgoland_reproduction_inputs.json").read_text()
        )
        rows = MODULE.build_downloads(manifest, Path("/remote-data"))
        self.assertEqual(len(rows), 62)
        self.assertEqual(len({row.url for row in rows}), 62)
        self.assertTrue(rows[0].destination.name.startswith("HELG00DEU"))
        self.assertIn("/026/", rows[0].url)
        self.assertTrue(rows[-1].destination.name.startswith("HEL200DEU"))
        self.assertIn("/056/", rows[-1].url)


if __name__ == "__main__":
    unittest.main()
