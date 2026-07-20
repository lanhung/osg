from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.build_paper1_jog_release import _scan_sources, _validate_submission_metadata

ROOT = Path(__file__).resolve().parents[2]


def test_journal_source_has_no_visible_draft_markers() -> None:
    _scan_sources()


def test_incomplete_submission_metadata_blocks_release() -> None:
    metadata = json.loads(
        (ROOT / "papers/paper1_journal_of_geodesy/submission_metadata.json").read_text()
    )
    assert metadata["status"] != "complete_verified"
    with pytest.raises(RuntimeError, match="not complete and verified"):
        _validate_submission_metadata()
    candidate = _validate_submission_metadata(require_release=False)
    assert candidate["corresponding_author_email"] == "f.zhang@zju.edu.cn"
