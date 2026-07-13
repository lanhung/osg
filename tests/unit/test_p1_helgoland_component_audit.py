"""Helgoland component decomposition preserves the published observable boundary."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "run_p1_helgoland_component_audit",
    ROOT / "scripts/run_p1_helgoland_component_audit.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_component_audit_reproduces_registered_elastic_ratio_and_separation() -> None:
    config = json.loads((ROOT / "configs/paper1/helgoland_component_audit.json").read_text())
    source = json.loads(
        (ROOT / "experiments/paper1/P1-E005-helgoland-bsh-model/metrics.json").read_text()
    )
    result = MODULE.run(config, source)
    assert result["sample_count"] == 720
    assert result["published_elastic_comparison"]["model_nm_s2_per_mm"] == pytest.approx(
        -2.2662457310207795
    )
    assert result["component_scale_ratios"]["direct_to_elastic_rms"] == pytest.approx(
        0.18025498474152382
    )
    assert not result["diagnostic_total_proximity"]["comparison_authorized"]
    assert all(
        row["quantitative_allocation"] is None for row in result["discrepancy_source_ledger"]
    )
