"""Frozen query tests for Paper 3 real-noise window candidates."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "fetch_p3_noise_windows", ROOT / "scripts/fetch_p3_noise_windows.py"
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _requests() -> tuple[dict, ...]:
    document = json.loads((ROOT / "data/manifests/paper3_noise_window_requests.json").read_text())
    return MODULE.build_requests(document)


def test_requests_cover_five_stations_and_three_disjoint_windows() -> None:
    rows = _requests()
    assert len(rows) == 15
    assert len({(row["network"], row["station"]) for row in rows}) == 5
    assert len({row["window_id"] for row in rows}) == 3
    assert all(len(row["channels"]) == 3 for row in rows)


def test_blank_locations_use_fdsn_double_dash() -> None:
    rows = _requests()
    blank = [row for row in rows if row["station"] in {"HKPS", "KKM", "KMNB"}]
    assert blank
    assert all(row["location"] == "--" for row in blank)
    assert all("loc=--" in row["requested_url"] for row in blank)


def test_candidate_roles_do_not_claim_quiet_data() -> None:
    assert all("quiet" not in row["label_status"] for row in _requests())
