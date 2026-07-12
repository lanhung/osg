"""Submission-policy tests for unavailable published-case observations."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from audit_p1_published_case_submission_gate import audit  # noqa: E402


def test_repository_policy_passes_on_open_helgoland_model_case() -> None:
    policy = json.loads((ROOT / "configs/paper1/published_case_submission_policy.json").read_text())
    result = audit(policy)
    assert result["status"] == "pass"
    assert result["passing_open_model_cases"] == 1
    assert all(
        row["status"] == "disclosed_unavailable"
        for row in result["supporting_external_dependencies"]
    )


def test_policy_rejects_external_dependency_relabelled_as_blocking() -> None:
    policy = json.loads((ROOT / "configs/paper1/published_case_submission_policy.json").read_text())
    policy["supporting_external_dependencies"][0]["blocks_main_atlas"] = True
    try:
        audit(policy)
    except ValueError as error:
        assert "must not silently block" in str(error)
    else:
        raise AssertionError("blocking relabel must be rejected")
