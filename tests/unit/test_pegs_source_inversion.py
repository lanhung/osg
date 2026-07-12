"""Discrete PEGS source-library inversion tests."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.pegs import (  # noqa: E402
    SourceTemplateHypothesis,
    invert_discrete_source_library,
)


def _hypothesis(identifier: str, magnitude: float, segment: str, amplitude: float):
    return SourceTemplateHypothesis(
        identifier,
        magnitude,
        segment,
        f"fixture:{identifier}",
        {"A": (amplitude, -amplitude), "B": (0.5 * amplitude, -0.5 * amplitude)},
    )


class TestPegsSourceInversion(unittest.TestCase):
    def test_exact_library_member_recovers_magnitude_and_segment(self) -> None:
        hypotheses = (
            _hypothesis("north-82", 8.2, "north", 1.0),
            _hypothesis("central-86", 8.6, "central", 2.0),
        )
        result = invert_discrete_source_library(
            {"A": (2.0, -2.0), "B": (1.0, -1.0)},
            hypotheses,
            {"A": 1.0, "B": 1.0},
            {"A": "quiet:A", "B": "quiet:B"},
            source_library_id="fixture-library-v1",
            sample_interval_s=1.0,
            window_start_time_since_origin_s=240.0,
        )
        self.assertEqual(result.best_scenario_id, "central-86")
        self.assertEqual(result.estimated_magnitude_mw, 8.6)
        self.assertEqual(result.estimated_segment_id, "central")
        self.assertEqual(result.best_chi_square, 0.0)
        self.assertTrue(result.best_beats_null)
        self.assertTrue(result.best_is_unique)
        self.assertGreater(result.second_best_delta_chi_square, 0.0)

    def test_candidate_worse_than_null_is_not_a_detection(self) -> None:
        result = invert_discrete_source_library(
            {"A": (0.0,), "B": (0.0,)},
            (SourceTemplateHypothesis("large", 9.0, "joint", "fixture:large", {"A": (5.0,), "B": (5.0,)}),),
            {"A": 1.0, "B": 1.0},
            {"A": "quiet:A", "B": "quiet:B"},
            source_library_id="fixture-library-v1",
            sample_interval_s=1.0,
            window_start_time_since_origin_s=240.0,
        )
        self.assertFalse(result.best_beats_null)
        self.assertEqual(result.second_best_delta_chi_square, None)

    def test_mask_is_shared_by_all_hypotheses(self) -> None:
        result = invert_discrete_source_library(
            {"A": (1.0, 100.0), "B": (0.5, 100.0)},
            (_hypothesis("target", 8.2, "north", 1.0),),
            {"A": 1.0, "B": 1.0},
            {"A": "quiet:A", "B": "quiet:B"},
            source_library_id="fixture-library-v1",
            sample_interval_s=2.0,
            window_start_time_since_origin_s=240.0,
            station_inclusion_masks={"A": (True, False), "B": (True, False)},
        )
        self.assertEqual(result.best_chi_square, 0.0)
        self.assertEqual(result.included_sample_count, 2)

    def test_duplicate_scenarios_and_station_mismatch_fail(self) -> None:
        row = _hypothesis("same", 8.2, "north", 1.0)
        with self.assertRaisesRegex(ValueError, "unique"):
            invert_discrete_source_library(
                {"A": (1.0, -1.0), "B": (0.5, -0.5)},
                (row, row),
                {"A": 1.0, "B": 1.0},
                {"A": "quiet:A", "B": "quiet:B"},
                source_library_id="fixture-library-v1",
                sample_interval_s=1.0,
                window_start_time_since_origin_s=240.0,
            )
        bad = SourceTemplateHypothesis("bad", 8.2, "north", "fixture:bad", {"A": (1.0, -1.0)})
        with self.assertRaisesRegex(ValueError, "do not match"):
            invert_discrete_source_library(
                {"A": (1.0, -1.0), "B": (0.5, -0.5)},
                (bad,),
                {"A": 1.0, "B": 1.0},
                {"A": "quiet:A", "B": "quiet:B"},
                source_library_id="fixture-library-v1",
                sample_interval_s=1.0,
                window_start_time_since_origin_s=240.0,
            )

    def test_provenance_and_physical_time_are_recorded(self) -> None:
        result = invert_discrete_source_library(
            {"A": (1.0, -1.0), "B": (0.5, -0.5)},
            (_hypothesis("target", 8.2, "north", 1.0),),
            {"A": 1.0, "B": 1.0},
            {"A": "quiet:A", "B": "quiet:B"},
            source_library_id="fixture-library-v1",
            sample_interval_s=0.5,
            window_start_time_since_origin_s=240.0,
        )
        self.assertEqual(result.window_duration_s, 1.0)
        self.assertEqual(result.window_start_time_since_origin_s, 240.0)
        self.assertEqual(result.decision_time_since_origin_s, 241.0)
        self.assertEqual(result.source_library_id, "fixture-library-v1")
        self.assertEqual(result.ranked_hypotheses[0].template_source_id, "fixture:target")

    def test_negative_or_nonfinite_window_start_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "window_start_time"):
            invert_discrete_source_library(
                {"A": (1.0,), "B": (0.5,)},
                (_hypothesis("target", 8.2, "north", 1.0),),
                {"A": 1.0, "B": 1.0},
                {"A": "quiet:A", "B": "quiet:B"},
                source_library_id="fixture-library-v1",
                sample_interval_s=1.0,
                window_start_time_since_origin_s=-1.0,
            )

    def test_tied_best_hypotheses_are_not_claimed_as_unique(self) -> None:
        result = invert_discrete_source_library(
            {"A": (1.0, -1.0), "B": (0.5, -0.5)},
            (
                _hypothesis("north", 8.2, "north", 1.0),
                _hypothesis("central", 8.2, "central", 1.0),
            ),
            {"A": 1.0, "B": 1.0},
            {"A": "quiet:A", "B": "quiet:B"},
            source_library_id="fixture-library-v1",
            sample_interval_s=1.0,
            window_start_time_since_origin_s=240.0,
        )
        self.assertEqual(result.second_best_delta_chi_square, 0.0)
        self.assertFalse(result.best_is_unique)


if __name__ == "__main__":
    unittest.main()
