"""Release-boundary tests for Paper 3 open waveform network citations."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _document() -> dict:
    return json.loads((ROOT / "data/manifests/paper3_network_citations.json").read_text())


def test_every_evaluation_network_has_operator_and_citation_disposition() -> None:
    rows = _document()["networks"]
    assert {row["network"] for row in rows} == {"HK", "IC", "IU", "MY", "TW"}
    assert all(row["operator"].strip() and row["fdsn_url"].startswith("https://") for row in rows)
    assert {row["doi"] for row in rows if row["doi"]} == {
        "10.7914/SN/IC",
        "10.7914/SN/IU",
        "10.7914/SN/TW",
    }


def test_unresolved_licences_keep_raw_redistribution_closed() -> None:
    rows = _document()["networks"]
    assert all(row["raw_redistribution_authorized"] is False for row in rows)
    assert "keep MiniSEED and StationXML off Git" in _document()["release_policy"]
