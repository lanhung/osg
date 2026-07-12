"""Single-station PEGS energy-baseline tests."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.evaluation import QuietScoreWindow
from oceangravity.pegs import (
    audit_single_station_energy_baseline,
    windowed_rms_energy_scores,
)


class TestPegsEnergyBaseline(unittest.TestCase):
    def test_window_rms_and_step_are_explicit(self) -> None:
        result = windowed_rms_energy_scores(
            (3.0, 4.0, 0.0, 0.0, 6.0, 8.0),
            window_length_samples=2,
            decision_step_samples=2,
        )
        self.assertEqual(result.scores, (math.sqrt(12.5), 0.0, math.sqrt(50.0)))
        self.assertEqual(result.start_sample_indices, (0, 2, 4))
        self.assertEqual(result.trailing_samples_after_last_start, 0)

    def test_mask_discards_whole_windows_without_compaction(self) -> None:
        result = windowed_rms_energy_scores(
            range(7),
            window_length_samples=3,
            decision_step_samples=2,
            inclusion_mask=(True, True, True, False, True, True, True),
        )
        self.assertEqual(result.start_sample_indices, (0, 4))
        self.assertEqual(result.discarded_start_sample_indices, (2,))
        self.assertEqual(result.trailing_samples_after_last_start, 0)

    def test_threshold_is_frozen_before_heldout_event_scoring(self) -> None:
        quiets = (
            QuietScoreWindow("cal", "threshold_calibration", (1.0, 1.1, 1.2), 60.0),
            QuietScoreWindow("quiet-test", "held_out", (0.9, 1.0, 1.1), 60.0),
        )
        result = audit_single_station_energy_baseline(
            quiets,
            {"event-b": (1.0, 2.0, 3.0), "event-a": (2.0, 2.0)},
            target_false_alarms_per_30_days=1.0,
        )
        self.assertGreater(result.quiet_false_positive_audit.threshold.threshold, 1.2)
        self.assertEqual(
            tuple(row.event_id for row in result.heldout_events), ("event-a", "event-b")
        )
        self.assertEqual(result.heldout_events[0].triggered_score_fraction, 1.0)
        self.assertEqual(result.heldout_events[0].earliest_trigger_score_index, 0)
        self.assertEqual(result.heldout_events[1].triggered_score_fraction, 2.0 / 3.0)
        self.assertEqual(result.heldout_events[1].earliest_trigger_score_index, 1)

    def test_invalid_masks_and_identity_leakage_fail(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least one"):
            windowed_rms_energy_scores(
                (1.0, 2.0, 3.0),
                window_length_samples=2,
                decision_step_samples=1,
                inclusion_mask=(False, False, True),
            )
        quiets = (
            QuietScoreWindow("same", "threshold_calibration", (1.0,), 60.0),
            QuietScoreWindow("held", "held_out", (1.0,), 60.0),
        )
        with self.assertRaisesRegex(ValueError, "overlap"):
            audit_single_station_energy_baseline(
                quiets,
                {"same": (2.0,)},
                target_false_alarms_per_30_days=1.0,
            )


if __name__ == "__main__":
    unittest.main()
