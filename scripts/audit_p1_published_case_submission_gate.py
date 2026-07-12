"""Audit the Paper 1 published-case gate with declared external exceptions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _nested(document: dict, dotted_path: str):
    value = document
    for key in dotted_path.split("."):
        value = value[key]
    return value


def audit(policy: dict, root: Path = ROOT) -> dict:
    if policy.get("schema_version") != 1:
        raise ValueError("unsupported submission-policy schema version")
    cases = []
    for row in policy["open_model_cases"]:
        path = root / row["experiment_metrics"]
        metrics = json.loads(path.read_text(encoding="utf-8"))
        actual = _nested(metrics, row["status_path"])
        cases.append(
            {
                "case_id": row["case_id"],
                "experiment_id": metrics["experiment_id"],
                "actual_status": actual,
                "required_status": row["required_status"],
                "status": "pass" if actual == row["required_status"] else "fail",
            }
        )
    passing = sum(row["status"] == "pass" for row in cases)
    dependencies = []
    for row in policy["supporting_external_dependencies"]:
        if row["blocks_main_atlas"]:
            raise ValueError(
                "supporting external dependencies must not silently block the main atlas"
            )
        dependencies.append({**row, "status": "disclosed_unavailable"})
    status = "pass" if passing >= policy["minimum_passing_open_model_cases"] else "fail"
    return {
        "schema_version": 1,
        "policy_id": policy["policy_id"],
        "status": status,
        "passing_open_model_cases": passing,
        "minimum_passing_open_model_cases": policy["minimum_passing_open_model_cases"],
        "open_model_cases": cases,
        "supporting_external_dependencies": dependencies,
        "interpretation": (
            "The published-case submission gate passes for the main atlas; unavailable "
            "observation statistics remain prohibited rather than imputed."
            if status == "pass"
            else "The main atlas lacks the required passing open model case."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--policy",
        type=Path,
        default=ROOT / "configs/paper1/published_case_submission_policy.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "reports/p1_published_case_submission_gate.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = audit(json.loads(args.policy.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
