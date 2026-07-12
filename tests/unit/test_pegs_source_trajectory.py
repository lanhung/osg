"""Time-dependent discrete PEGS source-trajectory tests."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.pegs import (  # noqa: E402
    SourceTemplateHypothesis,
    invert_discrete_source_library_over_time,
)


def _hypothesis(identifier, magnitude, segment, values):
    return SourceTemplateHypothesis(
        identifier, magnitude, segment, f"fixture:{identifier}", {"A": values}
    )


class TestPegsSourceTrajectory(unittest.TestCase):
    def test_prefix_rankings_change_at_explicit_decision_times(self) -> None:
        result = invert_discrete_source_library_over_time(
            {"A": (0.5, -0.5, 1.0, -1.0)},
            (
                _hypothesis("early-small", 8.2, "north", (0.5, -0.5, 0.0, 0.0)),
                _hypothesis("late-large", 8.6, "central", (0.1, -0.1, 1.0, -1.0)),
            ),
            {"A": 1.0},
            {"A": "quiet-A"},
            source_library_id="fixture-library-v1",
            sample_interval_s=1.0,
            window_start_time_since_origin_s=10.0,
            decision_sample_counts=(2, 4),
        )
        self.assertEqual(
            tuple(point.best_scenario_id for point in result.points),
            ("early-small", "late-large"),
        )
        self.assertEqual(
            tuple(point.decision_time_since_origin_s for point in result.points),
            (12.0, 14.0),
        )
        self.assertEqual(
            result.interpretation,
            "prefix_library_ranking_not_reliable_magnitude_without_heldout_gates",
        )

    def test_masks_are_sliced_without_compaction(self) -> None:
        result = invert_discrete_source_library_over_time(
            {"A": (1.0, 50.0, -1.0)},
            (_hypothesis("target", 8.2, "north", (1.0, 0.0, -1.0)),),
            {"A": 1.0},
            {"A": "quiet-A"},
            source_library_id="fixture-library-v1",
            sample_interval_s=2.0,
            window_start_time_since_origin_s=0.0,
            decision_sample_counts=(1, 3),
            station_inclusion_masks={"A": (True, False, True)},
        )
        self.assertEqual(
            tuple(point.included_sample_count for point in result.points), (1, 2)
        )
        self.assertEqual(result.points[-1].improvement_over_null_chi_square, 2.0)

    def test_decision_counts_are_strict_and_bounded(self) -> None:
        arguments = dict(
            station_observations={"A": (1.0, 2.0)},
            hypotheses=(_hypothesis("one", 8.0, "north", (1.0, 2.0)),),
            station_noise_standard_deviation={"A": 1.0},
            station_noise_scale_source_ids={"A": "quiet-A"},
            source_library_id="library",
            sample_interval_s=1.0,
            window_start_time_since_origin_s=0.0,
        )
        with self.assertRaisesRegex(ValueError, "strictly increasing"):
            invert_discrete_source_library_over_time(
                **arguments, decision_sample_counts=(1, 1)
            )
        with self.assertRaisesRegex(ValueError, "exceeds"):
            invert_discrete_source_library_over_time(
                **arguments, decision_sample_counts=(3,)
            )


if __name__ == "__main__":
    unittest.main()
