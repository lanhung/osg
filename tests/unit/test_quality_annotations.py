"""Non-destructive Paper 2 annotation and exclusion-policy tests."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from oceangravity.signal_processing import (  # noqa: E402
    DataQualityAnnotation,
    apply_quality_annotations,
)


def _policy():
    document = json.loads((ROOT / "configs/paper2/exclusion_policy.json").read_text())
    return document["policy_id"], document["actions"]


class TestQualityAnnotations(unittest.TestCase):
    def test_annotations_preserve_values_and_separate_fit_metric_masks(self) -> None:
        times = tuple(f"2024-01-01T0{hour}:00:00Z" for hour in range(4))
        annotations = (
            DataQualityAnnotation(
                "candidate",
                "candidate_spike",
                times[0],
                times[1],
                "threshold",
                "unclassified discontinuity",
            ),
            DataQualityAnnotation(
                "edge",
                "gap_edge_buffer",
                times[1],
                times[2],
                "gap manifest",
                "filter edge sensitivity",
            ),
            DataQualityAnnotation(
                "quake",
                "earthquake",
                times[2],
                times[3],
                "reviewed catalogue",
                "regional earthquake",
            ),
        )
        policy_id, actions = _policy()
        result = apply_quality_annotations(
            times, (1.0, 2.0, 3.0, 4.0), annotations, actions, policy_id=policy_id
        )
        self.assertEqual(result.original_values, (1.0, 2.0, 3.0, 4.0))
        self.assertEqual(result.fit_included, (True, False, False, True))
        self.assertEqual(result.metric_included, (True, True, False, True))
        self.assertEqual(result.annotation_ids_by_sample[0], ("candidate",))

    def test_overlapping_flags_apply_most_restrictive_action(self) -> None:
        times = ("2024-01-01T00:00:00Z", "2024-01-01T01:00:00Z")
        rows = (
            DataQualityAnnotation(
                "candidate", "candidate_spike", times[0], times[1], "a", "a"
            ),
            DataQualityAnnotation(
                "maintenance", "maintenance", times[0], times[1], "b", "b"
            ),
        )
        policy_id, actions = _policy()
        result = apply_quality_annotations(
            times, (1.0, 2.0), rows, actions, policy_id=policy_id
        )
        self.assertFalse(result.fit_included[0])
        self.assertFalse(result.metric_included[0])
        self.assertEqual(
            result.annotation_ids_by_sample[0], ("candidate", "maintenance")
        )

    def test_incomplete_policy_and_unmatched_annotation_are_rejected(self) -> None:
        times = ("2024-01-01T00:00:00Z",)
        row = DataQualityAnnotation(
            "future",
            "maintenance",
            "2025-01-01T00:00:00Z",
            "2025-01-02T00:00:00Z",
            "log",
            "fixture",
        )
        policy_id, actions = _policy()
        with self.assertRaisesRegex(ValueError, "matches no samples"):
            apply_quality_annotations(times, (1.0,), (row,), actions, policy_id=policy_id)
        incomplete = dict(actions)
        incomplete.pop("earthquake")
        with self.assertRaisesRegex(ValueError, "match exactly"):
            apply_quality_annotations(times, (1.0,), (), incomplete, policy_id=policy_id)

    def test_policy_is_frozen_before_comparison(self) -> None:
        document = json.loads((ROOT / "configs/paper2/exclusion_policy.json").read_text())
        self.assertEqual(document["status"], "frozen-before-event-model-comparison")
        self.assertEqual(document["actions"]["candidate_spike"], "retain")
        self.assertEqual(
            document["actions"]["confirmed_instrument_spike"],
            "exclude_from_fit_and_metrics",
        )


if __name__ == "__main__":
    unittest.main()
