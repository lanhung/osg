"""Observable-separation tests for deterministic instrument SVGs."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

from render_instrument_noise_curves import render_observable  # noqa: E402

from oceangravity.instruments import load_noise_curves  # noqa: E402


class TestRenderInstrumentCurves(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.curves = list(
            load_noise_curves(ROOT / "data/manifests/instrument_noise_curves.json").values()
        )

    def test_vertical_panel_excludes_gradient_instruments(self) -> None:
        svg = render_observable(self.curves, "vertical_gravity")
        self.assertIn("igrav_quiet_j9_self_noise_anchor", svg)
        self.assertIn("aqg_a01_field_short_term_anchor", svg)
        self.assertNotIn("mcguirk_atom_gradiometer_anchor", svg)
        self.assertIn("m s^-2 Hz^-1/2", svg)

    def test_gradient_panel_excludes_gravimeters(self) -> None:
        svg = render_observable(self.curves, "gravity_gradient")
        self.assertIn("mcguirk_atom_gradiometer_anchor", svg)
        self.assertIn("goce_egg_conservative_design_anchor", svg)
        self.assertNotIn("igrav_quiet_j9_self_noise_anchor", svg)
        self.assertIn("s^-2 Hz^-1/2", svg)

    def test_unknown_observable_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            render_observable(self.curves, "unknown")


if __name__ == "__main__":
    unittest.main()
