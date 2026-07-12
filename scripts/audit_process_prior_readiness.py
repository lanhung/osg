"""Refuse production ensembles until every process has a frozen joint design."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def audit_document(document: dict) -> dict:
    if document.get("schema_version") != 1:
        raise ValueError("unsupported process-evidence schema version")
    processes = document.get("processes")
    if not isinstance(processes, dict) or not processes:
        raise ValueError("process evidence must contain processes")
    results = []
    for process_id, process in sorted(processes.items()):
        evidence = process.get("evidence", [])
        unresolved = process.get("unresolved_for_atlas", [])
        design = process.get("production_joint_design")
        blockers = []
        if not evidence:
            blockers.append("no_traceable_evidence")
        if unresolved:
            blockers.append("unresolved_physics_or_parameter_fields")
        if not isinstance(design, dict) or design.get("status") != "frozen":
            blockers.append("missing_frozen_production_joint_design")
        elif design.get("semantics") not in {
            "probability_prior",
            "sensitivity_design_not_probability",
        }:
            blockers.append("invalid_joint_design_semantics")
        elif not design.get("parameters"):
            blockers.append("empty_joint_design")
        results.append(
            {
                "process_id": process_id,
                "evidence_count": len(evidence),
                "unresolved_count": len(unresolved),
                "production_joint_design_status": (
                    design.get("status") if isinstance(design, dict) else "missing"
                ),
                "ready_for_production_ensemble": not blockers,
                "blockers": blockers,
            }
        )
    return {
        "schema_version": 1,
        "all_processes_ready": all(
            row["ready_for_production_ensemble"] for row in results
        ),
        "ready_count": sum(row["ready_for_production_ensemble"] for row in results),
        "process_count": len(results),
        "processes": results,
        "policy": "Foundation fixtures may run, but production atlas ensembles require this gate to pass for all six processes.",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "data/manifests/process_parameter_evidence.json",
    )
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = audit_document(json.loads(args.manifest.read_text()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
