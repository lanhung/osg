"""Evaluate the frozen Paper 2 environmental-effect composition ledger."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from oceangravity.loading import EffectDeclaration, audit_effect_ledger  # noqa: E402


def audit_document(document: dict) -> dict:
    if document.get("schema_version") != 1:
        raise ValueError("unsupported effect-composition schema version")
    audit = audit_effect_ledger(
        tuple(EffectDeclaration(**row) for row in document["declarations"]),
        required_effect_ids=document["required_effect_ids"],
    )
    return {
        "schema_version": 1,
        "closure_ready": audit.closure_ready,
        "effects": [asdict(row) for row in audit.effects],
        "resolution_action": document["resolution_action"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/paper2/effect_composition.json",
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
