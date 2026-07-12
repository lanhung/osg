"""Pure contract tests for the Paper 3 open noise-window pipeline."""

from __future__ import annotations

import importlib.util
import itertools
import math
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]


def _module(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


FETCH = _module("fetch_p3_noise_windows", "scripts/fetch_p3_noise_windows.py")
AUDIT = _module("audit_p3_noise_windows", "scripts/audit_p3_noise_windows.py")


def test_blank_location_is_encoded_as_fdsn_double_dash() -> None:
    import json

    config = json.loads((ROOT / "data/manifests/paper3_noise_window_requests.json").read_text())
    rows = FETCH.build_requests(config)
    blank = [row for row in rows if row["station"] == "HKPS"]
    assert blank
    assert all("loc=--" in row["requested_url"] for row in blank)
    assert all("LHE%2CLHN%2CLHZ" in row["requested_url"] for row in blank)


def test_diagnostic_band_metric_recovers_sine_rms_order() -> None:
    times = np.arange(8192, dtype=float)
    low = np.sin(2.0 * math.pi * 0.01 * times)
    doubled = 2.0 * low
    first = AUDIT.diagnostic_band_metrics(low, 1.0, (0.005, 0.05))
    second = AUDIT.diagnostic_band_metrics(doubled, 1.0, (0.005, 0.05))
    assert second["band_rms_m_s2"] == pytest.approx(2.0 * first["band_rms_m_s2"])


def test_request_windows_are_disjoint_and_unclassified() -> None:
    import json

    config = json.loads((ROOT / "data/manifests/paper3_noise_window_requests.json").read_text())
    intervals = sorted((row["start_utc"], row["end_utc"]) for row in config["windows"])
    assert all(left[1] <= right[0] for left, right in itertools.pairwise(intervals))
    assert all("quiet" not in row["label_status"] for row in config["windows"])
