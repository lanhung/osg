"""Contract tests for the Paper 1 evidence-bounded atlas runner."""

from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "run_p1_evidence_bounded_atlas", ROOT / "scripts/run_p1_evidence_bounded_atlas.py"
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_midpoint_designs_do_not_include_unregistered_endpoints() -> None:
    assert MODULE._linear_midpoints([0.0, 10.0], 2) == (2.5, 7.5)
    values = MODULE._log_midpoints([1.0, 100.0], 2)
    assert math.isclose(values[0], math.sqrt(10.0))
    assert math.isclose(values[1], 10.0 * math.sqrt(10.0))


def test_config_uses_evidence_manifest_sample_counts() -> None:
    config = json.loads((ROOT / "configs/paper1/evidence_bounded_atlas.json").read_text())
    evidence = json.loads((ROOT / "data/manifests/process_parameter_evidence.json").read_text())[
        "processes"
    ]
    assert (
        config["tide"]["sample_count"]
        == evidence["tide"]["production_joint_design"]["sample_count"]
    )
    assert (
        config["internal_wave"]["sample_count"]
        == evidence["internal_wave"]["production_joint_design"]["sample_count"]
    )
    assert (
        config["tsunami"]["sample_count"]
        == evidence["tsunami"]["production_joint_design"]["sample_count"]
    )


def test_only_vertical_gravity_curves_are_authorized() -> None:
    config = json.loads((ROOT / "configs/paper1/evidence_bounded_atlas.json").read_text())
    manifest = json.loads((ROOT / config["instrument_curve_manifest"]).read_text())
    observables = {row["instrument_id"]: row["observable"] for row in manifest["curves"]}
    assert all(
        observables[curve_id] == "vertical_gravity"
        for curve_id in config["authorized_vertical_gravity_curves"]
    )
