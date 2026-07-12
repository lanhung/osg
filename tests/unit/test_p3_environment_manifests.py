import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_environment_audit_keeps_quiet_gate_closed() -> None:
    audit = json.loads(
        (ROOT / "data/manifests/paper3_noise_environment_audit_2026-07-12.json").read_text()
    )
    assert audit["summary"]["window_count"] == 5
    assert audit["summary"]["quiet_label_count"] == 0
    assert all(item["environment_label_status"].startswith("pending_") for item in audit["windows"])


def test_long_noise_stage1_exposure_and_split_independence() -> None:
    manifest = json.loads(
        (ROOT / "data/manifests/paper3_long_noise_stage1_requests.json").read_text()
    )
    assert len(manifest["stations"]) == 5
    assert len(manifest["windows"]) == 8
    calibration = [
        window for window in manifest["windows"] if "calibration" in window["split_role"]
    ]
    heldout = [window for window in manifest["windows"] if "heldout" in window["split_role"]]
    assert len(calibration) == len(heldout) == 4
    assert {window["start_utc"][:4] for window in calibration} == {"2023"}
    assert {window["start_utc"][:4] for window in heldout} == {"2025"}
    assert manifest["stage_gates"]["stage1_total_station_days_requested"] == 40
    assert manifest["processing"]["diagnostic_band_hz"] == [0.005, 0.05]
    assert manifest["processing"]["maximum_start_phase_mismatch_samples"] == 0.001


def test_dynamic_values_are_not_promoted_to_manila_defaults() -> None:
    sources = json.loads((ROOT / "data/manifests/manila_scenario_sources.json").read_text())
    audit = sources["dynamic_parameter_literature_audit"]
    assert audit["rupture_velocity"]["scenario_default_authorized"] is False
    assert audit["rise_time"]["scenario_default_authorized"] is False
    assert audit["rise_time"]["manila_specific_value_s"] is None


def test_stage1_catalogue_rules_match_pilot_audit() -> None:
    pilot = json.loads((ROOT / "configs/paper3/noise_environment_audit.json").read_text())
    stage1 = json.loads((ROOT / "configs/paper3/noise_environment_stage1_audit.json").read_text())
    assert stage1["earthquake_catalog"]["candidate_rules"] == pilot["earthquake_catalog"][
        "candidate_rules"
    ]
