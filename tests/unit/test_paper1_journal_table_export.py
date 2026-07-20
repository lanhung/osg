from __future__ import annotations

import json
from pathlib import Path

from scripts.export_paper1_journal_tables import (
    frequency_requirement_table,
    instrument_evidence_table,
    process_parameter_table,
    record_registry_table,
)

ROOT = Path(__file__).resolve().parents[2]


def test_generated_tables_are_populated_from_frozen_inputs() -> None:
    config = json.loads((ROOT / "configs/paper1/evidence_bounded_atlas.json").read_text())
    metrics = json.loads(
        (
            ROOT / "experiments/paper1/P1-E008-frequency-coverage-requirements/metrics.json"
        ).read_text()
    )
    instruments = json.loads(
        (ROOT / "data/manifests/instrument_noise_curves_reviewed_v2.json").read_text()
    )
    assert "M2 period" in process_parameter_table(config)
    assert "storm\\_surge" in record_registry_table(metrics)
    assert "$f_{90}$ median" in frequency_requirement_table(metrics)
    assert "aqg\\_a01" in instrument_evidence_table(instruments)
