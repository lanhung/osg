"""Helgoland BSH-HBMnoku structural-audit tests."""

from __future__ import annotations

import importlib.util
import unittest
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "audit_helgoland_bsh_hbmnoku",
    ROOT / "scripts/audit_helgoland_bsh_hbmnoku.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class TestHelgolandBshAudit(unittest.TestCase):
    def test_source_time_offset_is_canonicalized_within_tolerance(self) -> None:
        cycle = datetime(2022, 1, 26, tzinfo=UTC)
        expected = np.arange(
            np.datetime64("2022-01-26T00:15:00", "ns"),
            np.datetime64("2022-01-26T06:15:00", "ns"),
            np.timedelta64(15, "m"),
        )
        actual = expected + np.timedelta64(288, "ms")
        canonical, error = MODULE.audit_time_axis(actual, cycle, 24, 15, 360, 0.5)
        np.testing.assert_array_equal(canonical, expected)
        self.assertAlmostEqual(error, 0.288)

    def test_excessive_time_offset_is_rejected(self) -> None:
        cycle = datetime(2022, 1, 26, tzinfo=UTC)
        actual = np.arange(
            np.datetime64("2022-01-26T00:15:01", "ns"),
            np.datetime64("2022-01-26T06:15:01", "ns"),
            np.timedelta64(15, "m"),
        )
        with self.assertRaisesRegex(ValueError, "canonicalization tolerance"):
            MODULE.audit_time_axis(actual, cycle, 24, 15, 360, 0.5)


if __name__ == "__main__":
    unittest.main()
