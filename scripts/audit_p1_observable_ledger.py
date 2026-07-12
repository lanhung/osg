"""Audit Paper 1 observable labels, units, artifacts and figure coverage."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

REQUIRED_COLUMNS = (
    "output_id",
    "artifact_path",
    "process_scope",
    "direct",
    "elastic_potential",
    "height",
    "total",
    "instrument_comparison_allowed",
    "units",
    "manuscript_location",
    "required_label",
    "release_disposition",
)


def audit(root: Path, ledger_path: Path, figure_manifest_path: Path) -> dict:
    with ledger_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != REQUIRED_COLUMNS:
            raise ValueError("observable ledger columns do not match frozen schema")
        rows = list(reader)
    if len({row["output_id"] for row in rows}) != len(rows):
        raise ValueError("observable output IDs must be unique")
    missing_artifacts = sorted(
        row["artifact_path"] for row in rows if not (root / row["artifact_path"]).is_file()
    )
    incomplete_rows = sorted(
        row["output_id"]
        for row in rows
        if any(not row[column].strip() for column in REQUIRED_COLUMNS)
    )
    figure_manifest = json.loads((root / figure_manifest_path).read_text())
    ledger_artifacts = {row["artifact_path"] for row in rows}
    missing_figure_rows = sorted(
        item["path"] for item in figure_manifest["figures"] if item["path"] not in ledger_artifacts
    )
    unqualified_production_labels = sorted(
        row["output_id"]
        for row in rows
        if "gravity" in row["required_label"].lower()
        and not any(
            term in row["required_label"].lower()
            for term in ("direct", "elastic", "gradient", "total")
        )
    )
    return {
        "schema_version": 1,
        "ledger_row_count": len(rows),
        "missing_artifacts": missing_artifacts,
        "incomplete_rows": incomplete_rows,
        "missing_figure_rows": missing_figure_rows,
        "unqualified_production_labels": unqualified_production_labels,
        "main_output_count": sum("main" in row["release_disposition"] for row in rows),
        "audit_passes": not any(
            (
                missing_artifacts,
                incomplete_rows,
                missing_figure_rows,
                unqualified_production_labels,
            )
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--figure-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.root, args.ledger, args.figure_manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
