"""Dependency-free tests for physical constants and unit conversions."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.constants import (  # noqa: E402
    GRAVITATIONAL_CONSTANT,
    MICROGAL,
    NANOMETRE_PER_SECOND_SQUARED,
    microgal_to_si,
    si_to_microgal,
)


class TestPhysicalConstants(unittest.TestCase):
    def test_gravitational_constant_is_si_and_positive(self) -> None:
        self.assertEqual(GRAVITATIONAL_CONSTANT.unit, "m^3 kg^-1 s^-2")
        self.assertGreater(GRAVITATIONAL_CONSTANT.value, 0.0)

    def test_microgal_definition(self) -> None:
        self.assertEqual(MICROGAL, 1.0e-8)
        self.assertEqual(microgal_to_si(1.0), 1.0e-8)

    def test_nm_per_second_squared_relation(self) -> None:
        self.assertEqual(NANOMETRE_PER_SECOND_SQUARED, 1.0e-9)
        self.assertAlmostEqual(microgal_to_si(0.1), NANOMETRE_PER_SECOND_SQUARED)

    def test_microgal_round_trip(self) -> None:
        for value in (-12.0, 0.0, 2.6, 120.0):
            with self.subTest(value=value):
                self.assertAlmostEqual(si_to_microgal(microgal_to_si(value)), value)


if __name__ == "__main__":
    unittest.main()

