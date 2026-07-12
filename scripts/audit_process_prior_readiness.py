"""Refuse production ensembles until every process has a frozen joint design."""

from __future__ import annotations

import argparse
import json
import math
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
        else:
            semantics = design.get("semantics")
            if semantics not in {
                "probability_prior",
                "sensitivity_design_not_probability",
            }:
                blockers.append("invalid_joint_design_semantics")
            if not isinstance(design.get("sample_count"), int) or isinstance(
                design.get("sample_count"), bool
            ) or design.get("sample_count", 0) <= 0:
                blockers.append("invalid_sample_count")
            if not isinstance(design.get("random_seed"), int) or isinstance(
                design.get("random_seed"), bool
            ):
                blockers.append("missing_integer_random_seed")
            variants = design.get("model_variants")
            if not isinstance(variants, list) or not variants or any(
                not isinstance(item, str) or not item.strip() for item in variants
            ):
                blockers.append("missing_model_variants")
            if not isinstance(design.get("joint_constraints"), list):
                blockers.append("missing_joint_constraints")

            parameters = design.get("parameters")
            if not isinstance(parameters, dict) or not parameters:
                blockers.append("empty_joint_design")
            else:
                evidence_by_parameter = {
                    item.get("parameter"): item
                    for item in evidence
                    if isinstance(item, dict) and item.get("parameter")
                }
                for parameter_name, specification in parameters.items():
                    if not isinstance(specification, dict):
                        blockers.append(f"invalid_parameter_specification:{parameter_name}")
                        continue
                    unit = specification.get("unit")
                    scale = specification.get("scale")
                    bounds = specification.get("range")
                    references = specification.get("evidence_parameters")
                    if not isinstance(unit, str) or not unit.strip():
                        blockers.append(f"missing_parameter_unit:{parameter_name}")
                    if scale not in {"linear", "log"}:
                        blockers.append(f"invalid_parameter_scale:{parameter_name}")
                    if not (
                        isinstance(bounds, list)
                        and len(bounds) == 2
                        and all(
                            isinstance(value, (int, float))
                            and not isinstance(value, bool)
                            and math.isfinite(value)
                            for value in bounds
                        )
                        and bounds[0] < bounds[1]
                    ):
                        blockers.append(f"invalid_parameter_range:{parameter_name}")
                    elif scale == "log" and bounds[0] <= 0.0:
                        blockers.append(f"nonpositive_log_range:{parameter_name}")
                    if not isinstance(references, list) or not references:
                        blockers.append(f"missing_parameter_evidence:{parameter_name}")
                        continue
                    missing = [item for item in references if item not in evidence_by_parameter]
                    if missing:
                        blockers.append(f"unknown_parameter_evidence:{parameter_name}")
                    if semantics == "probability_prior" and any(
                        not evidence_by_parameter[item].get("probability_prior_eligible", False)
                        for item in references
                        if item in evidence_by_parameter
                    ):
                        blockers.append(f"nonprobabilistic_evidence_in_prior:{parameter_name}")
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
