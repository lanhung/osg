from __future__ import annotations

import json
from pathlib import Path

from scripts.run_p1_evidence_bounded_atlas import run

ROOT = Path(__file__).resolve().parents[2]


def test_optional_temporal_controls_preserve_frozen_e006_output() -> None:
    config = json.loads((ROOT / "configs/paper1/evidence_bounded_atlas.json").read_text())
    expected = json.loads(
        (ROOT / "experiments/paper1/P1-E006-evidence-bounded-atlas/metrics.json").read_text()
    )
    assert run(config) == expected
