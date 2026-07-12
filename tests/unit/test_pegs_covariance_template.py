"""Cross-station covariance PEGS template tests."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.pegs import (
    CrossStationCovarianceModel,
    cross_station_covariance_template_scores,
    estimate_cross_station_covariance,
    independent_noise_network_template_scores,
)


class TestPegsCovarianceTemplate(unittest.TestCase):
    def test_diagonal_covariance_matches_independent_noise_score(self) -> None:
        series = {"A": (2.0, -2.0), "B": (1.0, -1.0)}
        templates = {"A": (1.0, -1.0), "B": (0.5, -0.5)}
        independent = independent_noise_network_template_scores(
            series,
            templates,
            {"A": 2.0, "B": 0.5},
            {"A": "quiet-A", "B": "quiet-B"},
            sample_interval_s=1.0,
            decision_step_samples=1,
        )
        covariance = CrossStationCovarianceModel(
            ("A", "B"),
            ((4.0, 0.0), (0.0, 0.25)),
            "quiet-covariance-v1",
            ("quiet-A", "quiet-B"),
        )
        correlated = cross_station_covariance_template_scores(
            series,
            templates,
            covariance,
            sample_interval_s=1.0,
            decision_step_samples=1,
        )
        self.assertAlmostEqual(correlated.scores[0], independent.scores[0])

    def test_positive_common_noise_reduces_equal_station_gain(self) -> None:
        series = {"A": (1.0,), "B": (1.0,)}
        templates = {"A": (1.0,), "B": (1.0,)}
        independent = CrossStationCovarianceModel(
            ("A", "B"), ((1.0, 0.0), (0.0, 1.0)), "independent", ("q",)
        )
        correlated = CrossStationCovarianceModel(
            ("A", "B"), ((1.0, 0.8), (0.8, 1.0)), "correlated", ("q",)
        )
        first = cross_station_covariance_template_scores(
            series, templates, independent, sample_interval_s=1.0, decision_step_samples=1
        )
        second = cross_station_covariance_template_scores(
            series, templates, correlated, sample_interval_s=1.0, decision_step_samples=1
        )
        self.assertAlmostEqual(first.scores[0], math.sqrt(2.0))
        self.assertLess(second.scores[0], first.scores[0])

    def test_non_positive_definite_and_station_mismatch_fail(self) -> None:
        with self.assertRaisesRegex(ValueError, "positive definite"):
            CrossStationCovarianceModel(("A", "B"), ((1.0, 1.0), (1.0, 1.0)), "bad", ("q",))
        covariance = CrossStationCovarianceModel(("A",), ((1.0,),), "one", ("q",))
        with self.assertRaisesRegex(ValueError, "match covariance"):
            cross_station_covariance_template_scores(
                {"B": (1.0,)},
                {"B": (1.0,)},
                covariance,
                sample_interval_s=1.0,
                decision_step_samples=1,
            )

    def test_masks_are_not_compacted(self) -> None:
        covariance = CrossStationCovarianceModel(
            ("A", "B"), ((1.0, 0.0), (0.0, 1.0)), "cov", ("quiet",)
        )
        result = cross_station_covariance_template_scores(
            {"A": range(5), "B": range(5)},
            {"A": (1.0, 1.0), "B": (1.0, 1.0)},
            covariance,
            sample_interval_s=1.0,
            decision_step_samples=1,
            station_inclusion_masks={
                "A": (True,) * 5,
                "B": (True, True, False, True, True),
            },
        )
        self.assertEqual(result.start_sample_indices, (0, 3))
        self.assertEqual(result.discarded_start_sample_indices, (1, 2))

    def test_covariance_estimation_uses_complete_quiet_samples_and_shrinkage(self) -> None:
        model = estimate_cross_station_covariance(
            {
                "quiet-2": {"A": (1.0, -1.0), "B": (1.0, -1.0)},
                "quiet-1": {"A": (1.0, -1.0), "B": (1.0, -1.0)},
            },
            source_id="quiet-cov-v1",
            diagonal_shrinkage=0.5,
            minimum_complete_samples=4,
        )
        self.assertEqual(model.calibration_window_ids, ("quiet-1", "quiet-2"))
        self.assertEqual(model.complete_sample_count, 4)
        self.assertEqual(model.estimation_method, "complete_case_unbiased_diagonal_shrinkage")
        self.assertAlmostEqual(model.covariance[0][0], 4.0 / 3.0)
        self.assertAlmostEqual(model.covariance[0][1], 2.0 / 3.0)

    def test_covariance_estimation_rejects_insufficient_complete_cases(self) -> None:
        with self.assertRaisesRegex(ValueError, "below minimum"):
            estimate_cross_station_covariance(
                {"quiet": {"A": (1.0, 2.0), "B": (1.0, 2.0)}},
                source_id="quiet-cov-v1",
                diagonal_shrinkage=0.5,
                minimum_complete_samples=2,
                inclusion_masks={"quiet": {"A": (True, False), "B": (True, True)}},
            )


if __name__ == "__main__":
    unittest.main()
