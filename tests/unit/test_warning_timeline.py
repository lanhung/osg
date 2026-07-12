"""Sign and location tests for PEGS warning metrics."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.pegs import WarningTimeline


class TestWarningTimeline(unittest.TestCase):
    def test_gain_and_lead_sign_conventions(self) -> None:
        timeline = WarningTimeline(
            p_trigger_s=120.0,
            pegs_detect_s=90.0,
            pegs_reliable_magnitude_s=300.0,
            conventional_reliable_magnitude_s=900.0,
            tsunami_arrivals_s=(("hong_kong", 10_800.0), ("hainan_east", 7_200.0)),
        )
        self.assertEqual(timeline.characterization_gain_s, 600.0)
        self.assertEqual(timeline.pegs_detection_relative_to_p_trigger_s, -30.0)
        self.assertEqual(
            timeline.lead_times_s(),
            {"hong_kong": 10_500.0, "hainan_east": 6_900.0},
        )

    def test_negative_gain_is_retained_not_relabelled(self) -> None:
        timeline = WarningTimeline(
            p_trigger_s=10.0,
            pegs_detect_s=200.0,
            pegs_reliable_magnitude_s=1_000.0,
            conventional_reliable_magnitude_s=800.0,
            tsunami_arrivals_s=(("site", 5_000.0),),
        )
        self.assertEqual(timeline.characterization_gain_s, -200.0)

    def test_invalid_ordering_and_duplicate_locations_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            WarningTimeline(10.0, 100.0, 99.0, 200.0, (("site", 1_000.0),))
        with self.assertRaises(ValueError):
            WarningTimeline(
                10.0,
                100.0,
                200.0,
                300.0,
                (("site", 1_000.0), ("site", 2_000.0)),
            )


if __name__ == "__main__":
    unittest.main()
