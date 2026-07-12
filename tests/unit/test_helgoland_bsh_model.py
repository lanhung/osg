"""Numerical-contract tests for the Helgoland conservative remap runner."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "run_helgoland_bsh_model", ROOT / "scripts/run_helgoland_bsh_model.py"
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_coordinate_edges_accept_descending_centres() -> None:
    edges = MODULE.coordinate_edges(np.array([2.5, 1.5, 0.5]))
    np.testing.assert_allclose(edges, [0.0, 1.0, 2.0, 3.0])


def test_interval_overlap_conserves_domain_width() -> None:
    operator = MODULE.interval_overlap_matrix(
        np.array([0.0, 1.5, 3.0]), np.array([0.0, 1.0, 2.0, 3.0])
    )
    np.testing.assert_allclose(np.asarray(operator.sum(axis=1)).ravel(), [1.5, 1.5])
    np.testing.assert_allclose(np.asarray(operator.sum(axis=0)).ravel(), [1.0, 1.0, 1.0])


def test_separable_remap_conserves_constant_field_integral() -> None:
    source_lat = np.array([0.5, 1.5])
    source_lon = np.array([10.5, 11.5])
    target_lat = np.array([0.0, 2.0])
    target_lon = np.array([10.0, 12.0])
    latitude, longitude, _, reverse = MODULE.build_remap_operators(
        source_lat, source_lon, target_lat, target_lon
    )
    integral = MODULE.conservative_integrated_field(
        np.ones((2, 2)), latitude, longitude, reverse_latitude=bool(reverse[0])
    )
    expected = (
        MODULE._ellipsoid_area_coordinate(np.array([0.0, 2.0]))[1]
        - MODULE._ellipsoid_area_coordinate(np.array([0.0, 2.0]))[0]
    ) * np.radians(2.0)
    np.testing.assert_allclose(integral, [[expected]], rtol=2e-15)


def test_load_green_table_ignores_headers_and_footer(tmp_path: Path) -> None:
    table = tmp_path / "ce.txt"
    table.write_text(
        "header\n"
        "0.1 -2e-12 0 0 0 -10 0\n"
        "0.2 -1e-12 0 0 0 -8 0\n"
        "footer has more than six non numeric tokens here\n",
        encoding="utf-8",
    )
    theta, gravity, displacement = MODULE._load_green_table(table, 6_371_000.0)
    np.testing.assert_allclose(theta, np.radians([0.1, 0.2]))
    np.testing.assert_allclose(displacement, [-2e-12, -1e-12])
    np.testing.assert_allclose(
        gravity,
        np.array([-10.0, -8.0]) / (1e18 * 6_371_000.0 * theta),
    )
