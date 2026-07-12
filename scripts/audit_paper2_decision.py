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
    interval = document.get("ocean_coefficient_confidence_interval")
    evidence = Paper2DecisionEvidence(
        uses_real_observations=document["uses_real_observations"],
        data_gate_passes=document["data_gate_passes"],
        analysis_complete=document["analysis_complete"],
        typhoon_event_count=document["typhoon_event_count"],
        heldout_event_count=document["heldout_event_count"],
        quiet_window_count=document["quiet_window_count"],
        effect_closure_ready=document["effect_closure_ready"],
        direct_deformation_separated=document["direct_deformation_separated"],
        multi_source_validation_complete=document["multi_source_validation_complete"],
        sensitivity_analysis_complete=document["sensitivity_analysis_complete"],
        failed_event_log_complete=document["failed_event_log_complete"],
        data_license_review_complete=document["data_license_review_complete"],
        ocean_coefficient_confidence_interval=(
            None if interval is None else (float(interval[0]), float(interval[1]))
        ),
        heldout_improvement_passes=tuple(document["heldout_improvement_passes"]),
        heldout_quiet_far_passes=document["heldout_quiet_far_passes"],
        event_snrs=tuple(float(value) for value in document["event_snrs"]),
        minimum_interpretable_event_snr=float(
            document["minimum_interpretable_event_snr"]
        ),
    )
    audit = audit_paper2_decision(evidence)
    result = asdict(audit)
    result["schema_version"] = 1
    result["evidence_status"] = document["evidence_status"]
    result["novelty_requirements"] = dict(audit.novelty_requirements)
    result["gates"] = dict(audit.gates)
    return result


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
