"""Helgoland BSH-HBMnoku download-plan tests."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "download_helgoland_bsh_hbmnoku",
    ROOT / "scripts/download_helgoland_bsh_hbmnoku.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class TestHelgolandBshDownload(unittest.TestCase):
    def test_registered_plan_has_both_grids_and_inclusive_bounds(self) -> None:
        manifest = json.loads(
            (ROOT / "data/manifests/helgoland_reproduction_inputs.json").read_text()
        )
        rows = MODULE.build_downloads(manifest, Path("/remote-data"))
        self.assertEqual(len(rows), 242)
        self.assertEqual({row.grid for row in rows}, {"fine", "coarse"})
        self.assertEqual(rows[0].cycle_utc, "2022-01-26T00:00:00Z")
        self.assertEqual(rows[-1].cycle_utc, "2022-02-25T00:00:00Z")
        self.assertEqual(len({row.url for row in rows}), 242)


if __name__ == "__main__":
    unittest.main()
