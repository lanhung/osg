"""Frequency-support requirements are coverage quantities, not detectability."""

from __future__ import annotations

import math

import pytest

from oceangravity.signal_processing import low_frequency_coverage_requirements


def test_single_bin_sinusoid_returns_its_resolved_frequency() -> None:
    count = 128
    interval = 1.0
    frequency = 8.0 / (count * interval)
    values = tuple(math.cos(2.0 * math.pi * frequency * index) for index in range(count))
    results = low_frequency_coverage_requirements(values, interval, (0.5, 0.9, 0.95))
    assert all(result.upper_frequency_sufficient for result in results)
    lower_edges = [result.maximum_admissible_low_frequency_hz for result in results]
    assert lower_edges[0] == pytest.approx(frequency)
    assert lower_edges == sorted(lower_edges, reverse=True)
    assert all(
        result.achieved_energy_fraction >= result.required_energy_fraction for result in results
    )


def test_insufficient_upper_edge_is_reported_without_extrapolation() -> None:
    count = 128
    values = tuple(math.cos(2.0 * math.pi * 0.25 * index) for index in range(count))
    (result,) = low_frequency_coverage_requirements(
        values,
        1.0,
        (0.9,),
        maximum_frequency_hz=0.1,
    )
    assert not result.upper_frequency_sufficient
    assert result.maximum_admissible_low_frequency_hz is None
    assert result.achieved_energy_fraction < 0.9


def test_thresholds_must_be_unique_and_increasing() -> None:
    with pytest.raises(ValueError, match="unique and increasing"):
        low_frequency_coverage_requirements((0.0, 1.0, 0.0, -1.0), 1.0, (0.9, 0.5))
