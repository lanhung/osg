"""Contract tests for the Paper 3 open-archive network design."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "run_p3_archive_network_design", ROOT / "scripts/run_p3_archive_network_design.py"
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _result() -> dict:
    config = json.loads((ROOT / "configs/paper3/archive_network_design.json").read_text())
    return MODULE.run(config)


def test_open_archive_network_passes_without_operational_claim() -> None:
    result = _result()
    assert result["status"] == "pass"
    assert result["noise_download_ready"] is True
    assert result["operational_warning_ready"] is False
    assert result["pegs_detectability_ready"] is False
    assert len(result["existing_archive_evaluation_network"]) == 5


def test_outage_design_freezes_zero_twenty_forty_percent_sets() -> None:
    rows = _result()["outage_design"]
    assert [row["outage_fraction"] for row in rows] == [0.0, 0.2, 0.4]
    assert [row["active_station_count"] for row in rows] == [5, 4, 3]
    assert [row["network_variant_count"] for row in rows] == [1, 5, 10]


def test_every_selected_station_has_open_lh_triplet_and_response() -> None:
    for row in _result()["existing_archive_evaluation_network"]:
        assert row["triplet"]["band"] == "LH"
        assert row["triplet"]["all_open"] is True
        assert row["triplet"]["sample_rate_hz"] >= 1.0
