"""Completeness tests for distance-attenuation SVG panels."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from render_distance_attenuation import render_metric  # noqa: E402


class TestRenderDistanceAttenuation(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads(
            (
                ROOT
                / "experiments/paper1/P1-E004-distance-attenuation-foundation/metrics.json"
            ).read_text()
        )

    def test_gravity_panel_contains_every_process(self) -> None:
        svg = render_metric(
            self.document,
            "peak_absolute_direct_gravity_m_s2",
            "Peak direct vertical gravity (m s^-2)",
        )
        for name in self.document["processes"]:
            self.assertIn(name, svg)
        self.assertIn("Vertical standoff (m)", svg)

    def test_gradient_panel_uses_Tzz_units(self) -> None:
        svg = render_metric(
            self.document,
            "peak_absolute_direct_Tzz_s2",
            "Peak absolute Tzz (s^-2)",
        )
        self.assertIn("Tzz (s^-2)", svg)


if __name__ == "__main__":
    unittest.main()
