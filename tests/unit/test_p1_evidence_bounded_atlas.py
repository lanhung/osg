"""Contract tests for the Paper 1 evidence-bounded atlas runner."""

from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "run_p1_evidence_bounded_atlas", ROOT / "scripts/run_p1_evidence_bounded_atlas.py"
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_midpoint_designs_do_not_include_unregistered_endpoints() -> None:
    assert MODULE._linear_midpoints([0.0, 10.0], 2) == (2.5, 7.5)
    values = MODULE._log_midpoints([1.0, 100.0], 2)
    assert math.isclose(values[0], math.sqrt(10.0))
    assert math.isclose(values[1], 10.0 * math.sqrt(10.0))


def test_config_uses_evidence_manifest_sample_counts() -> None:
    config = json.loads((ROOT / "configs/paper1/evidence_bounded_atlas.json").read_text())
    evidence = json.loads((ROOT / "data/manifests/process_parameter_evidence.json").read_text())[
        "processes"
    ]
    assert (
        config["tide"]["sample_count"]
        == evidence["tide"]["production_joint_design"]["sample_count"]
    )
    assert (
        config["internal_wave"]["sample_count"]
        == evidence["internal_wave"]["production_joint_design"]["sample_count"]
    )
    assert (
        config["tsunami"]["sample_count"]
        == evidence["tsunami"]["production_joint_design"]["sample_count"]
    )


def test_only_vertical_gravity_curves_are_authorized() -> None:
    config = json.loads((ROOT / "configs/paper1/evidence_bounded_atlas.json").read_text())
    manifest = json.loads((ROOT / config["instrument_curve_manifest"]).read_text())
    observables = {row["instrument_id"]: row["observable"] for row in manifest["curves"]}
    assert all(
        observables[curve_id] == "vertical_gravity"
        for curve_id in config["authorized_vertical_gravity_curves"]
    )


def test_spherical_disk_response_is_bounded_and_attractive() -> None:
    surface_density = 1025.0
    near = MODULE._spherical_disk_response(
        radius_m=100_000.0,
        station_standoff_m=10_000.0,
        surface_density_kg_m2=surface_density,
    )
    far = MODULE._spherical_disk_response(
        radius_m=100_000.0,
        station_standoff_m=1_000_000.0,
        surface_density_kg_m2=surface_density,
    )
    infinite_sheet_bound = 2.0 * math.pi * 6.67430e-11 * surface_density
    assert -infinite_sheet_bound < near < 0.0
    assert abs(far) < abs(near)


def test_spherical_gaussian_mass_normalization_closes() -> None:
    target_mass = 1.0e15
    _, mass = MODULE._spherical_gaussian_patch_response(
        center_y_m=300_000.0,
        station_x_m=-200_000.0,
        scale_m=50_000.0,
        peak_surface_density_kg_m2=1025.0,
        cutoff_sigma=3.0,
        cells_per_sigma=8,
        target_signed_mass_kg=target_mass,
    )
    assert math.isclose(mass, target_mass, rel_tol=2e-15)
