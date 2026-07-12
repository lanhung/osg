"""Run the registered Paper 2 non-restricted readiness audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from audit_effect_composition import audit_document as audit_effects  # noqa: E402
from audit_paper2_data_gate import audit_manifest as audit_data_gate  # noqa: E402
from audit_paper2_decision import audit_document as audit_decision  # noqa: E402

from oceangravity.evaluation import canonicalize_report_floats  # noqa: E402


def _read(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def run(config: dict) -> dict:
    if config.get("schema_version") != 1:
        raise ValueError("unsupported Paper 2 readiness schema")
    inventory = _read(config["candidate_inventory"])
    data_gate = audit_data_gate(_read(config["event_data_manifest"]))
    effect_gate = audit_effects(_read(config["effect_composition"]))
    decision_gate = audit_decision(_read(config["decision_evidence"]))
    reports = tuple(config["required_method_reports"])
    missing_reports = tuple(path for path in reports if not (ROOT / path).is_file())
    priority = tuple(
        sorted(row["name"] for row in inventory["events"] if row["shortlist_screening_passes"])
    )
    canonical = json.dumps(config, sort_keys=True, separators=(",", ":"))
    return canonicalize_report_floats(
        {
            "schema_version": 1,
            "experiment_id": config["experiment_id"],
            "result_class": "nonrestricted_method_readiness_not_event_attribution",
            "config_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
            "method_artifact_gate": {
                "required_report_count": len(reports),
                "missing_reports": missing_reports,
                "status": "pass" if not missing_reports else "fail",
            },
            "open_candidate_inventory": {
                "candidate_count": inventory["candidate_count"],
                "priority_screening_count": len(priority),
                "priority_names": priority,
                "interpretation": "coverage inquiries only; not selected gravity events",
            },
            "event_data_gate": data_gate,
            "effect_composition_gate": effect_gate,
            "claim_decision_gate": decision_gate,
            "scientific_claim_ready": False,
            "nonrestricted_work_complete": (
                not missing_reports
                and data_gate["decision"] == "pending_no_event_windows"
                and not effect_gate["closure_ready"]
                and decision_gate["audit"]["branch"] == "pending_evidence"
            ),
            "external_dependencies": config["external_dependencies"],
            "interpretation_limits": [
                "No fixture or open storm track is an SG detection.",
                "A final event cannot be selected before real station coverage is intersected.",
                "Unknown CMEMS inverse-barometer semantics blocks effect closure "
                "independently of SG access.",
            ],
        },
        significant_digits=10,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run(json.loads(args.config.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
