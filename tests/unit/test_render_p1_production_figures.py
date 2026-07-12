"""Deterministic renderer tests for the Paper 1 production bundle."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "render_p1_production_figures", ROOT / "scripts/render_p1_production_figures.py"
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_frequency_ranges_place_long_period_processes_below_curves() -> None:
    config = json.loads((ROOT / "configs/paper1/evidence_bounded_atlas.json").read_text())
    ranges = MODULE._frequency_ranges(config)
    for process in ("tide", "storm_surge", "mesoscale_eddy", "internal_wave"):
        assert ranges[process][1] < 1e-3


def test_renderer_produces_four_nonempty_svg_assets(tmp_path: Path) -> None:
    metrics = json.loads(
        (ROOT / "experiments/paper1/P1-E006-evidence-bounded-atlas/metrics.json").read_text()
    )
    config = json.loads((ROOT / "configs/paper1/evidence_bounded_atlas.json").read_text())
    curves = json.loads((ROOT / "data/manifests/instrument_noise_curves.json").read_text())
    manifest = MODULE.run(metrics, config, curves, tmp_path)
    assert len(manifest["assets"]) == 4
    for row in manifest["assets"].values():
        path = ROOT / row["path"] if not row["path"].startswith("/") else Path(row["path"])
        if not path.exists():
            path = tmp_path / Path(row["path"]).name
        assert path.stat().st_size > 1000
        preview = Path(row["preview_png_path"])
        assert preview.stat().st_size > 1000
        assert row["status"] == "complete"
