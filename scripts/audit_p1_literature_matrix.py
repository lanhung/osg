"""Audit Paper 1 literature coverage, BibTeX linkage and review status."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

REQUIRED_COLUMNS = (
    "citation_key",
    "domain",
    "observable",
    "frequency_band",
    "instrument",
    "source_process",
    "data_or_model",
    "principal_result",
    "role_in_paper1",
    "claim_supported",
    "claim_not_supported",
    "full_text_reviewed",
)
PROCESS_TERMS = {
    "tide": ("ocean tide",),
    "storm_surge": ("storm surge", "storm surge/ntol"),
    "mesoscale_eddy": ("mesoscale eddy", "internal tide and eddy"),
    "internal_wave": ("internal wave", "internal tide", "internal tide and eddy"),
    "tsunami": ("tsunami",),
    "submarine_landslide": (
        "submarine landslide",
        "storegga landslide",
        "mediterranean landslides",
    ),
}


def audit(matrix_path: Path, bibliography_path: Path) -> dict:
    with matrix_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != REQUIRED_COLUMNS:
            raise ValueError("literature matrix columns do not match the frozen schema")
        rows = list(reader)
    keys = [row["citation_key"] for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("literature matrix citation keys must be unique")
    if any(row["full_text_reviewed"] not in {"yes", "no"} for row in rows):
        raise ValueError("full_text_reviewed must be yes or no")
    bib_text = bibliography_path.read_text(encoding="utf-8")
    bib_keys = set(re.findall(r"^@\w+\{([^,]+),", bib_text, flags=re.MULTILINE))
    missing_bib = sorted(set(keys) - bib_keys)
    process_counts = {
        process: sum(any(term in row["source_process"].lower() for term in terms) for row in rows)
        for process, terms in PROCESS_TERMS.items()
    }
    full_text_count = sum(row["full_text_reviewed"] == "yes" for row in rows)
    return {
        "schema_version": 1,
        "matrix_entry_count": len(rows),
        "bibliography_entry_count": len(bib_keys),
        "full_text_reviewed_count": full_text_count,
        "metadata_or_abstract_only_count": len(rows) - full_text_count,
        "missing_bibliography_keys": missing_bib,
        "domain_counts": dict(sorted(Counter(row["domain"] for row in rows).items())),
        "process_source_counts": process_counts,
        "minimum_reference_gate_passes": len(rows) >= 35 and not missing_bib,
        "full_text_gate_passes": full_text_count >= 35,
        "process_coverage_gate_passes": all(count >= 3 for count in process_counts.values()),
        "forbidden_placeholder_author_present": "and others" in bib_text.lower(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--bibliography", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.matrix, args.bibliography)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
