"""Multi-station PEGS template-statistic tests."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.pegs import independent_noise_network_template_scores


class TestPegsTemplateBaseline(unittest.TestCase):
    def test_equal_coherent_stations_gain_sqrt_n(self) -> None:
        one = independent_noise_network_template_scores(
            {"A": (1.0, -1.0)},
            {"A": (1.0, -1.0)},
            {"A": 1.0},
            {"A": "quiet-cal-A"},
            sample_interval_s=0.5,
            decision_step_samples=1,
        )
        two = independent_noise_network_template_scores(
            {"A": (1.0, -1.0), "B": (1.0, -1.0)},
            {"A": (1.0, -1.0), "B": (1.0, -1.0)},
            {"A": 1.0, "B": 1.0},
            {"A": "quiet-cal-A", "B": "quiet-cal-B"},
            sample_interval_s=0.5,
            decision_step_samples=1,
        )
        self.assertAlmostEqual(two.scores[0], math.sqrt(2.0) * one.scores[0])
        self.assertEqual(two.template_duration_s, 1.0)
        self.assertEqual(two.decision_step_s, 0.5)
        self.assertEqual(
            two.noise_scale_source_ids,
            (("A", "quiet-cal-A"), ("B", "quiet-cal-B")),
        )

    def test_physical_station_polarity_is_retained(self) -> None:
        aligned = independent_noise_network_template_scores(
            {"positive": (2.0, 0.0), "negative": (-2.0, 0.0)},
            {"positive": (1.0, 0.0), "negative": (-1.0, 0.0)},
            {"positive": 1.0, "negative": 1.0},
            {"positive": "quiet-positive", "negative": "quiet-negative"},
            sample_interval_s=1.0,
            decision_step_samples=1,
        )
        wrong_polarity = independent_noise_network_template_scores(
            {"positive": (2.0, 0.0), "negative": (-2.0, 0.0)},
            {"positive": (1.0, 0.0), "negative": (1.0, 0.0)},
            {"positive": 1.0, "negative": 1.0},
            {"positive": "quiet-positive", "negative": "quiet-negative"},
            sample_interval_s=1.0,
            decision_step_samples=1,
        )
        self.assertGreater(aligned.scores[0], 0.0)
        self.assertEqual(wrong_polarity.scores[0], 0.0)

    def test_any_station_mask_discards_the_network_window(self) -> None:
        result = independent_noise_network_template_scores(
            {"A": range(6), "B": range(6)},
            {"A": (1.0, 1.0), "B": (1.0, 1.0)},
            {"A": 1.0, "B": 1.0},
            {"A": "quiet-A", "B": "quiet-B"},
            sample_interval_s=1.0,
            decision_step_samples=2,
            station_inclusion_masks={
                "A": (True,) * 6,
                "B": (True, True, False, True, True, True),
            },
        )
        self.assertEqual(result.start_sample_indices, (0, 4))
        self.assertEqual(result.discarded_start_sample_indices, (2,))

    def test_station_identity_noise_and_zero_templates_are_strict(self) -> None:
        with self.assertRaisesRegex(ValueError, "match"):
            independent_noise_network_template_scores(
                {"A": (1.0,)},
                {"B": (1.0,)},
                {"A": 1.0},
                {"A": "quiet-A"},
                sample_interval_s=1.0,
                decision_step_samples=1,
            )
        with self.assertRaisesRegex(ValueError, "positive"):
            independent_noise_network_template_scores(
                {"A": (1.0,)},
                {"A": (1.0,)},
                {"A": 0.0},
                {"A": "quiet-A"},
                sample_interval_s=1.0,
                decision_step_samples=1,
            )
        with self.assertRaisesRegex(ValueError, "all be zero"):
            independent_noise_network_template_scores(
                {"A": (1.0,)},
                {"A": (0.0,)},
                {"A": 1.0},
                {"A": "quiet-A"},
                sample_interval_s=1.0,
                decision_step_samples=1,
            )

    def test_noise_provenance_and_sample_interval_are_required(self) -> None:
        with self.assertRaisesRegex(ValueError, "source IDs must match"):
            independent_noise_network_template_scores(
                {"A": (1.0,)},
                {"A": (1.0,)},
                {"A": 1.0},
                {},
                sample_interval_s=1.0,
                decision_step_samples=1,
            )
        with self.assertRaisesRegex(ValueError, "sample_interval_s"):
            independent_noise_network_template_scores(
                {"A": (1.0,)},
                {"A": (1.0,)},
                {"A": 1.0},
                {"A": "quiet-A"},
                sample_interval_s=0.0,
                decision_step_samples=1,
            )


if __name__ == "__main__":
    unittest.main()
