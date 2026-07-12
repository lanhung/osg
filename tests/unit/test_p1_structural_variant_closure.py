"""Contract tests for the Paper 1 structural-variant closure gate."""

from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "run_p1_structural_variant_closure",
    ROOT / "scripts/run_p1_structural_variant_closure.py",
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _config() -> dict:
    return json.loads((ROOT / "configs/paper1/structural_variant_closure.json").read_text())


def test_gate_closes_every_variant_without_external_dependencies() -> None:
    result = MODULE.run(_config())
    assert result["status"] == "pass"
    assert len(result["variant_decisions"]) == 7
    assert all(
        "IGETS" not in row["reason"] and "Haikou" not in row["reason"]
        for row in result["variant_decisions"]
    )


def test_energy_branch_is_mass_balanced_and_monotonic_in_energy() -> None:
    result = MODULE.run(_config())
    for row in result["implemented_energy_branch"]:
        amplitudes = row["crest_peak_sea_level_m"]
        assert amplitudes["energy_minus_uncertainty"] < amplitudes["central"]
        assert amplitudes["central"] < amplitudes["energy_plus_uncertainty"]
        assert row["packet_net_surface_mass_kg"] == 0.0


def test_gate_rejects_energy_not_registered_in_evidence() -> None:
    config = _config()
    config["tsunami_energy_branch"]["propagated_energy_j"] = math.nextafter(
        config["tsunami_energy_branch"]["propagated_energy_j"], math.inf
    )
    with pytest.raises(ValueError, match="evidence manifest"):
        MODULE.run(config)


def test_gate_rejects_duplicate_variant_ids() -> None:
    config = _config()
    config["variant_decisions"].append(dict(config["variant_decisions"][0]))
    with pytest.raises(ValueError, match="unique"):
        MODULE.run(config)
