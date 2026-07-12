"""Determinism and observable-safety tests for P1-E003."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from run_p1_gradient_detectability_foundation import run  # noqa: E402


class TestGradientDetectabilityExperiment(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = json.loads(
            (ROOT / "configs/paper1/gradient_detectability_foundation.json").read_text()
        )
        cls.result = run(cls.config)

    def test_result_is_deterministic_and_complete(self) -> None:
        self.assertEqual(self.result, run(self.config))
        self.assertEqual(len(self.result["matrix"]), 6)
        self.assertTrue(
            all(len(instruments) == 2 for instruments in self.result["matrix"].values())
        )

    def test_vertical_gravity_curves_are_explicitly_excluded(self) -> None:
        excluded = self.result["excluded_instrument_curves"]
        self.assertEqual(len(excluded), 3)
        self.assertTrue(all("vertical_gravity" in reason for reason in excluded.values()))

    def test_every_classification_obeys_coverage_gate(self) -> None:
        for instruments in self.result["matrix"].values():
            for item in instruments.values():
                if item["signal_energy_coverage_fraction"] < 0.9:
                    self.assertIn(
                        item["status"],
                        {"no_frequency_coverage", "partial_band_not_classified"},
                    )


if __name__ == "__main__":
    unittest.main()
