"""Contract tests for the Paper 2 non-restricted readiness experiment."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "run_p2_nonrestricted_readiness", ROOT / "scripts/run_p2_nonrestricted_readiness.py"
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _result() -> dict:
    config = json.loads((ROOT / "configs/paper2/nonrestricted_readiness.json").read_text())
    return MODULE.run(config)


def test_method_gate_passes_without_claiming_event_attribution() -> None:
    result = _result()
    assert result["method_artifact_gate"]["status"] == "pass"
    assert result["nonrestricted_work_complete"] is True
    assert result["scientific_claim_ready"] is False
    assert result["claim_decision_gate"]["audit"]["branch"] == "pending_evidence"


def test_open_candidates_remain_coverage_inquiries() -> None:
    result = _result()
    inventory = result["open_candidate_inventory"]
    assert inventory["candidate_count"] == 48
    assert inventory["priority_screening_count"] == 11
    assert "not selected gravity events" in inventory["interpretation"]


def test_pegs_is_not_a_paper2_dependency() -> None:
    assert _result()["external_dependencies"]["PEGS"] == "not a Paper 2 dependency"
