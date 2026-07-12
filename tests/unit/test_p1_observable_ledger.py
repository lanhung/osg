"""Machine-readable observable boundaries for every Paper 1 output."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "audit_p1_observable_ledger", ROOT / "scripts/audit_p1_observable_ledger.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_observable_ledger_covers_every_paper1_figure_and_has_units() -> None:
    result = MODULE.audit(
        ROOT,
        ROOT / "data/manifests/paper1_observable_ledger.csv",
        Path("papers/paper1_atlas/figure_manifest.json"),
    )
    assert result["ledger_row_count"] >= 10
    assert result["audit_passes"]
    assert not result["missing_artifacts"]
    assert not result["missing_figure_rows"]
    assert not result["unqualified_production_labels"]
