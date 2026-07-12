"""Canonical reporting helpers for cross-platform experiment artifacts."""

from __future__ import annotations

import math
from typing import Any


def canonicalize_report_floats(value: Any, *, significant_digits: int) -> Any:
    """Round finite report floats recursively to a declared precision.

    This is an output-boundary operation. Scientific calculations retain full
    precision; only machine-readable report values are canonicalized so harmless
    final-bit differences do not change registered artifact checksums.
    """

    if isinstance(significant_digits, bool) or not isinstance(significant_digits, int):
        raise TypeError("significant_digits must be an integer")
    if significant_digits < 1 or significant_digits > 16:
        raise ValueError("significant_digits must lie in [1, 16]")
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("report floats must be finite")
        if value == 0.0:
            return 0.0
        decimal_places = significant_digits - 1 - math.floor(math.log10(abs(value)))
        return round(value, decimal_places)
    if isinstance(value, dict):
        return {
            key: canonicalize_report_floats(item, significant_digits=significant_digits)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [
            canonicalize_report_floats(item, significant_digits=significant_digits)
            for item in value
        ]
    if isinstance(value, tuple):
        return tuple(
            canonicalize_report_floats(item, significant_digits=significant_digits)
            for item in value
        )
    return value
