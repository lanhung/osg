"""Generate a Paper 2 event/station data-closure decision from its manifest."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from oceangravity.evaluation import (  # noqa: E402
    EventStationData,
    EventWindow,
    audit_event_data_gate,
)


def audit_manifest(document: dict) -> dict:
    if document.get("schema_version") != 1:
        raise ValueError("unsupported manifest schema_version")
    decision_status = document.get("decision_status")
    if decision_status not in {"draft", "frozen"}:
        raise ValueError("decision_status must be draft or frozen")
    events = tuple(EventWindow(**row) for row in document.get("events", []))
    availability = tuple(
        EventStationData(**row) for row in document.get("station_data_availability", [])
    )
    if not events:
        if availability:
            raise ValueError("availability cannot exist without event windows")
        return {
            "schema_version": 1,
            "decision": "pending_no_event_windows",
            "decision_status": decision_status,
            "attribution_data_gate_passes": False,
            "audit": None,
        }
    audit = audit_event_data_gate(
        events,
        availability,
        minimum_gravity_coverage_fraction=float(document["minimum_gravity_coverage_fraction"]),
    )
    if decision_status == "draft":
        decision = "draft_pass" if audit.attribution_data_gate_passes else "draft_no_go"
    else:
        decision = (
            "go_full_attribution"
            if audit.attribution_data_gate_passes
            else "no_go_full_attribution"
        )
    return {
        "schema_version": 1,
        "decision": decision,
        "decision_status": decision_status,
        "attribution_data_gate_passes": audit.attribution_data_gate_passes,
        "audit": asdict(audit),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "data/manifests/paper2_event_windows.json",
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    document = json.loads(args.manifest.read_text())
    result = audit_manifest(document)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        sys.stdout.write(rendered)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
