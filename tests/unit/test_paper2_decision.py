"""Paper 2 claim-safe decision branch tests."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from oceangravity.evaluation import (  # noqa: E402
    Paper2DecisionEvidence,
    audit_paper2_decision,
)

SPEC = importlib.util.spec_from_file_location(
    "audit_paper2_decision", ROOT / "scripts/audit_paper2_decision.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def _complete() -> Paper2DecisionEvidence:
    return Paper2DecisionEvidence(
        uses_real_observations=True,
        analysis_complete=True,
        data_gate_passes=True,
        typhoon_event_count=4,
        heldout_event_count=1,
        quiet_window_count=4,
        effect_closure_ready=True,
        direct_deformation_separated=True,
        multi_source_validation_complete=True,
        sensitivity_analysis_complete=True,
        failed_event_log_complete=True,
        data_license_review_complete=True,
        attribution_ci_lower_bound=0.2,
        heldout_improvement_passes=(True,),
        heldout_quiet_far_passes=True,
        event_snrs=(5.0, 4.0, 6.0, 3.5),
        event_snr_interpretation_threshold=3.0,
    )


class TestPaper2Decision(unittest.TestCase):
    def test_complete_positive_evidence_allows_full_claim(self) -> None:
        result = audit_paper2_decision(_complete())
        self.assertEqual(result.branch, "successful_attribution")
        self.assertTrue(result.full_attribution_claim_ready)
        self.assertTrue(result.manuscript_release_ready)
        self.assertEqual(result.novelty.demonstrated_count, 4)
        self.assertEqual(result.blocking_reasons, ())

    def test_missing_license_blocks_release_not_scientific_branch(self) -> None:
        result = audit_paper2_decision(replace(_complete(), data_license_review_complete=False))
        self.assertEqual(result.branch, "successful_attribution")
        self.assertTrue(result.full_attribution_claim_ready)
        self.assertFalse(result.manuscript_release_ready)
        self.assertIn("data_license_review_incomplete", result.blocking_reasons)

    def test_complete_negative_result_uses_snr_to_select_failure_branch(self) -> None:
        negative = replace(
            _complete(),
            attribution_ci_lower_bound=-0.1,
            heldout_improvement_passes=(False,),
            event_snrs=(1.0, 1.5, 2.0, 2.5),
        )
        result = audit_paper2_decision(negative)
        self.assertEqual(result.branch, "non_detection_constraints")
        model_failure = audit_paper2_decision(replace(negative, event_snrs=(1.0, 1.5, 4.0, 2.5)))
        self.assertEqual(model_failure.branch, "ocean_product_evaluation")

    def test_missing_or_fixture_evidence_stays_pending(self) -> None:
        document = json.loads((ROOT / "configs/paper2/decision_evidence.json").read_text())
        result = MODULE.audit_document(document)
        self.assertEqual(result["audit"]["branch"], "pending_evidence")
        self.assertFalse(result["audit"]["full_attribution_claim_ready"])

    def test_incomplete_heldout_rows_cannot_be_treated_as_failure(self) -> None:
        result = audit_paper2_decision(
            replace(_complete(), heldout_event_count=2, heldout_improvement_passes=(False,))
        )
        self.assertEqual(result.branch, "pending_evidence")
        self.assertFalse(result.heldout_evaluation_complete)

    def test_single_case_requires_complete_case_evidence(self) -> None:
        case = replace(
            _complete(),
            typhoon_event_count=1,
            heldout_event_count=0,
            quiet_window_count=3,
            heldout_improvement_passes=(),
            event_snrs=(5.0,),
        )
        self.assertEqual(audit_paper2_decision(case).branch, "single_case_short_paper")
        incomplete = replace(case, effect_closure_ready=False)
        self.assertEqual(audit_paper2_decision(incomplete).branch, "pending_evidence")

    def test_invalid_counts_and_snr_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "cannot exceed"):
            replace(_complete(), heldout_event_count=5)
        with self.assertRaisesRegex(ValueError, "finite and non-negative"):
            replace(_complete(), event_snrs=(float("nan"),))


if __name__ == "__main__":
    unittest.main()
