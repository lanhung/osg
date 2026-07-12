"""Evaluate available Helgoland reproduction outputs against frozen targets."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from oceangravity.evaluation import CaseTarget, evaluate_case_reproduction  # noqa: E402


def evaluate_documents(configuration: dict, inputs: dict) -> dict:
    if configuration.get("schema_version") != 1 or inputs.get("schema_version") != 1:
        raise ValueError("unsupported Helgoland schema version")
    if configuration["case_id"] != inputs["case_id"]:
        raise ValueError("configuration and input case IDs differ")
    targets = tuple(
        CaseTarget(
            target_id=row["target_id"],
            expected_value=float(row["expected_value"]),
            unit=row["unit"],
            tolerance_kind=row["tolerance_kind"],
            tolerance=float(row["tolerance"]),
            source=row["source"],
        )
        for row in configuration["targets"]
    )
    audit = evaluate_case_reproduction(
        configuration["case_id"],
        targets,
        inputs.get("observed_reproduction_values", {}),
    )
    return {
        "schema_version": 1,
        "case_id": audit.case_id,
        "status": audit.status,
        "targets": [asdict(row) for row in audit.targets],
        "input_manifest_status": inputs["status"],
        "warning": "A pass requires outputs from the frozen method contract; scalar agreement from a simplified proxy is not a reproduction.",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/paper1/helgoland_reproduction.json",
    )
    parser.add_argument(
        "--inputs",
        type=Path,
        default=ROOT / "data/manifests/helgoland_reproduction_inputs.json",
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = evaluate_documents(
        json.loads(args.config.read_text()), json.loads(args.inputs.read_text())
    )
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        sys.stdout.write(rendered)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
