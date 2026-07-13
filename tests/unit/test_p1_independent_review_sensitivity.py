"""Tests for the Paper 1 independent-review sensitivity audit."""

from __future__ import annotations

import json
import math
import unittest
from pathlib import Path

from scripts.run_p1_independent_review_sensitivity import _parseval_requirements

ROOT = Path(__file__).resolve().parents[2]


class TestIndependentReviewSensitivity(unittest.TestCase):
    def test_parseval_requirement_recovers_exact_sinusoid_bin(self) -> None:
        count = 64
        interval = 1.0
        frequency = 5.0 / (count * interval)
        values = [math.cos(2.0 * math.pi * frequency * index * interval) for index in range(count)]
        result = _parseval_requirements(values, interval, (0.5, 0.9), window="rectangular")
        self.assertAlmostEqual(result["0.5"], frequency)
        self.assertAlmostEqual(result["0.9"], frequency)

    def test_reviewed_absolute_gravimeter_bands_follow_source_plateau(self) -> None:
        manifest = json.loads(
            (ROOT / "data/manifests/instrument_noise_curves_reviewed_v2.json").read_text()
        )
        by_id = {row["instrument_id"]: row for row in manifest["curves"]}
        for instrument in (
            "aqg_a01_field_short_term_anchor",
            "fg5_228_short_term_anchor",
        ):
            self.assertEqual(by_id[instrument]["frequencies_hz"], [0.0005, 0.01])
            self.assertIn("explicitly reported plateau", by_id[instrument]["interpretation"])


if __name__ == "__main__":
    unittest.main()
