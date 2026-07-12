"""Combine current published-case reproduction gates into one status artifact."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from evaluate_haikou_reproduction import evaluate_documents as evaluate_haikou
from evaluate_helgoland_reproduction import evaluate_documents as evaluate_helgoland


def _read(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text())


def audit_all_cases() -> dict:
    cases = [
        evaluate_helgoland(
            _read("configs/paper1/helgoland_reproduction.json"),
            _read("data/manifests/helgoland_reproduction_inputs.json"),
        ),
        evaluate_haikou(
            _read("configs/paper1/haikou_reproduction.json"),
            _read("data/manifests/haikou_reproduction_inputs.json"),
        ),
    ]
    status_counts = {
        status: sum(case["status"] == status for case in cases)
        for status in ("pass", "fail", "pending")
    }
    return {
        "schema_version": 1,
        "status_counts": status_counts,
        "all_required_cases_pass": all(case["status"] == "pass" for case in cases),
        "cases": cases,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = audit_all_cases()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
