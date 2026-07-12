"""Event-block bootstrap tests for the Paper 2 attribution coefficient."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.evaluation import bootstrap_ocean_attribution_by_event


class TestOceanAttributionBlockBootstrap(unittest.TestCase):
    def test_exact_relation_returns_exact_interval_and_is_deterministic(self) -> None:
        ocean = (0.0, 1.0, 2.0, 10.0, 11.0, 12.0, 20.0, 21.0, 22.0)
        baseline = (5.0,) * len(ocean)
        observed = tuple(5.0 + 2.0 + 3.0 * value for value in ocean)
        events = ("T1",) * 3 + ("T2",) * 3 + ("T3",) * 3
        first = bootstrap_ocean_attribution_by_event(
            observed,
            baseline,
            ocean,
            events,
            training_event_ids=("T3", "T1", "T2"),
            replicates=100,
            random_seed=17,
        )
        second = bootstrap_ocean_attribution_by_event(
            observed,
            baseline,
            ocean,
            events,
            training_event_ids=("T1", "T2", "T3"),
            replicates=100,
            random_seed=17,
        )
        self.assertEqual(first, second)
        self.assertAlmostEqual(first.confidence_interval[0], 3.0)
        self.assertAlmostEqual(first.confidence_interval[1], 3.0)
        self.assertAlmostEqual(first.median_ocean_coefficient, 3.0)
        self.assertEqual(first.valid_replicates, 100)
        self.assertEqual(first.training_event_ids, ("T1", "T2", "T3"))

    def test_mask_is_applied_before_complete_blocks_are_resampled(self) -> None:
        result = bootstrap_ocean_attribution_by_event(
            (1.0, 3.0, 999.0, 1.0, 3.0, 1.0, 3.0),
            (0.0,) * 7,
            (0.0, 1.0, 2.0, 0.0, 1.0, 0.0, 1.0),
            ("T1", "T1", "T1", "T2", "T2", "T3", "T3"),
            training_event_ids=("T1", "T2", "T3"),
            inclusion_mask=(True, True, False, True, True, True, True),
            replicates=20,
            random_seed=2,
        )
        self.assertTrue(
            all(value is None or abs(value - 2.0) < 1e-12 for value in result.ocean_coefficients)
        )

    def test_degenerate_draws_are_visible_and_can_fail_validity_gate(self) -> None:
        common = dict(
            observed_m_s2=(0.0, 1.0, 2.0),
            baseline_prediction_m_s2=(0.0, 0.0, 0.0),
            ocean_prediction_m_s2=(0.0, 1.0, 2.0),
            event_id_by_sample=("T1", "T2", "T3"),
            training_event_ids=("T1", "T2", "T3"),
            replicates=100,
            random_seed=3,
        )
        result = bootstrap_ocean_attribution_by_event(**common, minimum_valid_fraction=0.8)
        self.assertGreater(result.degenerate_replicates, 0)
        self.assertIn(None, result.ocean_coefficients)
        with self.assertRaisesRegex(ValueError, "valid event-block bootstrap fraction"):
            bootstrap_ocean_attribution_by_event(**common, minimum_valid_fraction=1.0)

    def test_three_events_and_nonempty_included_blocks_are_required(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least three"):
            bootstrap_ocean_attribution_by_event(
                (0.0, 1.0),
                (0.0, 0.0),
                (0.0, 1.0),
                ("T1", "T2"),
                training_event_ids=("T1", "T2"),
            )
        with self.assertRaisesRegex(ValueError, "no included samples"):
            bootstrap_ocean_attribution_by_event(
                (0.0, 1.0, 2.0),
                (0.0, 0.0, 0.0),
                (0.0, 1.0, 2.0),
                ("T1", "T2", "T3"),
                training_event_ids=("T1", "T2", "T3"),
                inclusion_mask=(True, True, False),
                replicates=10,
            )


if __name__ == "__main__":
    unittest.main()
