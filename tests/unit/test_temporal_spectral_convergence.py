from __future__ import annotations

import math

import pytest

from scripts.run_p1_temporal_spectral_convergence import (
    _dense_requirements,
    _relative_change,
)


def test_dense_requirement_converges_for_bin_centred_sinusoid() -> None:
    count = 64
    values = [math.sin(2.0 * math.pi * 4.0 * index / count) for index in range(count)]
    low, _, _ = _dense_requirements(values, 1.0, (0.9,), 16)
    high, _, _ = _dense_requirements(values, 1.0, (0.9,), 64)
    assert _relative_change(low["0.9"], high["0.9"]) < 0.05


def test_dense_requirement_rejects_zero_signal() -> None:
    with pytest.raises(ValueError, match="positive-frequency energy"):
        _dense_requirements([0.0] * 64, 1.0, (0.9,), 4)
