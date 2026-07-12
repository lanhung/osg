"""Render the claim-safe Paper 2 manuscript-branch decision."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from oceangravity.evaluation import (  # noqa: E402
    Paper2DecisionEvidence,
    audit_paper2_decision,
)


def audit_document(document: dict) -> dict:
    if document.get("schema_version") != 1:
        raise ValueError("unsupported Paper 2 decision-evidence schema version")
    evidence_document = document["evidence"]
    evidence = Paper2DecisionEvidence(
        uses_real_observations=evidence_document["uses_real_observations"],
        analysis_complete=evidence_document["analysis_complete"],
        data_gate_passes=evidence_document["data_gate_passes"],
        typhoon_event_count=evidence_document["typhoon_event_count"],
        heldout_event_count=evidence_document["heldout_event_count"],
        quiet_window_count=evidence_document["quiet_window_count"],
        effect_closure_ready=evidence_document["effect_closure_ready"],
        direct_deformation_separated=evidence_document["direct_deformation_separated"],
        multi_source_validation_complete=evidence_document["multi_source_validation_complete"],
        sensitivity_analysis_complete=evidence_document["sensitivity_analysis_complete"],
        failed_event_log_complete=evidence_document["failed_event_log_complete"],
        data_license_review_complete=evidence_document["data_license_review_complete"],
        attribution_ci_lower_bound=evidence_document["attribution_ci_lower_bound"],
        heldout_improvement_passes=tuple(evidence_document["heldout_improvement_passes"]),
        heldout_quiet_far_passes=evidence_document["heldout_quiet_far_passes"],
        event_snrs=tuple(float(value) for value in evidence_document["event_snrs"]),
        event_snr_interpretation_threshold=float(
            evidence_document["event_snr_interpretation_threshold"]
        ),
    )
    return {
        "schema_version": 1,
        "evidence_status": document["evidence_status"],
        "audit": asdict(audit_paper2_decision(evidence)),
        "provenance": document["provenance"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/paper2/decision_evidence.json",
    )
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = audit_document(json.loads(args.config.read_text()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
