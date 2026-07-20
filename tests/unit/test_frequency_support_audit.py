from __future__ import annotations

import pytest

from oceangravity.evaluation import (
    audit_curve_frequency_support,
    boundary_aware_spectral_energy,
)
from oceangravity.instruments import NoiseCurve


def _curve(lower: float, upper: float) -> NoiseCurve:
    return NoiseCurve(
        instrument_id="fixture",
        observable="vertical_gravity",
        asd_unit="m s^-2 Hz^-1/2",
        frequencies_hz=(lower, upper),
        asd=(1.0, 1.0),
        source="test fixture",
        curve_version="1",
    )


def test_support_audit_separates_nyquist_failure_from_grid_resolution() -> None:
    below = audit_curve_frequency_support(64, 10.0, _curve(0.1, 1.0))
    assert below.status == "source_temporal_support_below_curve"
    assert below.native_overlap_bin_count == 0

    unresolved = audit_curve_frequency_support(16, 1.0, _curve(0.08, 0.13))
    assert unresolved.status == "common_support_unresolved_by_native_grid"
    assert unresolved.native_overlap_bin_count == 1

    resolved = audit_curve_frequency_support(64, 1.0, _curve(0.08, 0.13))
    assert resolved.status == "native_common_support_resolved"
    assert resolved.native_overlap_bin_count >= 2


def test_boundary_aware_energy_integrates_partial_edge_intervals() -> None:
    frequencies = (1.0, 2.0, 3.0)
    amplitudes = (1.0 + 0j, 1.0 + 0j, 1.0 + 0j)
    assert boundary_aware_spectral_energy(frequencies, amplitudes, 1.5, 2.5) == pytest.approx(1.0)
    assert boundary_aware_spectral_energy(frequencies, amplitudes, 0.0, 1.5) == pytest.approx(0.5)
    assert boundary_aware_spectral_energy(frequencies, amplitudes, 4.0, 5.0) == 0.0
