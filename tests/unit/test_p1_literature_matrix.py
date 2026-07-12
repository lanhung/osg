"""Paper 1 structured literature and citation gates."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "audit_p1_literature_matrix", ROOT / "scripts/audit_p1_literature_matrix.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_literature_matrix_passes_reference_review_and_process_gates() -> None:
    result = MODULE.audit(
        ROOT / "docs/paper1_literature_matrix.csv",
        ROOT / "papers/paper1_atlas/references.bib",
    )
    assert result["matrix_entry_count"] >= 35
    assert result["bibliography_entry_count"] >= 35
    assert result["full_text_reviewed_count"] >= 35
    assert result["minimum_reference_gate_passes"]
    assert result["full_text_gate_passes"]
    assert result["process_coverage_gate_passes"]
    assert not result["missing_bibliography_keys"]
    assert not result["forbidden_placeholder_author_present"]
