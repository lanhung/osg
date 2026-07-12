"""Claim boundaries and aggregation checks for registered P1-E008."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_registered_frequency_requirement_result_is_complete_and_not_detectability() -> None:
    result = json.loads(
        (
            ROOT / "experiments/paper1/P1-E008-frequency-coverage-requirements/metrics.json"
        ).read_text()
    )
    assert result["record_count"] == 1446
    assert result["required_energy_fractions"] == [0.5, 0.75, 0.9, 0.95]
    assert result["result_class"] == "spectral_coverage_requirement_not_detectability"
    assert "detection probability" in result["claim_boundary"]
    assert set(result["process_summary"]) == {
        "tide",
        "storm_surge",
        "mesoscale_eddy",
        "internal_wave",
        "tsunami",
        "submarine_landslide",
    }


def test_every_process_requires_a_lower_edge_below_published_anchors() -> None:
    result = json.loads(
        (
            ROOT / "experiments/paper1/P1-E008-frequency-coverage-requirements/metrics.json"
        ).read_text()
    )
    for process in result["process_summary"].values():
        assert process["thresholds"]["0.9"]["median_hz"] < 1.0e-3
