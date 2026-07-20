from __future__ import annotations

from pathlib import Path

from scripts.audit_paper1_journal_consistency import audit

ROOT = Path(__file__).resolve().parents[2]


def test_paper1_journal_numbers_and_claims_match_registered_artifacts() -> None:
    result = audit(ROOT)
    assert result["audit_passes"], result["failures"]
