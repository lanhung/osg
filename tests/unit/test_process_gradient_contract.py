"""Ensure process signals expose gradients only when physically implemented."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.processes import ScalarGravitySignal


class TestProcessGradientContract(unittest.TestCase):
    def test_optional_gradient_validates_length_and_values(self) -> None:
        signal = ScalarGravitySignal(
            process_id="fixture",
            times_s=(0.0, 1.0),
            source_amplitude=(0.0, 1.0),
            source_amplitude_unit="1",
            vertical_direct_gravity_m_s2=(0.0, 2.0),
            model_scope="fixture",
            vertical_direct_gravity_gradient_s2=(0.0, 3.0),
        )
        self.assertEqual(signal.peak_absolute_gravity_gradient_s2, 3.0)
        with self.assertRaises(ValueError):
            ScalarGravitySignal(
                process_id="fixture",
                times_s=(0.0, 1.0),
                source_amplitude=(0.0, 1.0),
                source_amplitude_unit="1",
                vertical_direct_gravity_m_s2=(0.0, 2.0),
                model_scope="fixture",
                vertical_direct_gravity_gradient_s2=(0.0,),
            )

    def test_absent_gradient_remains_explicit_none(self) -> None:
        signal = ScalarGravitySignal(
            process_id="fixture",
            times_s=(0.0, 1.0),
            source_amplitude=(0.0, 1.0),
            source_amplitude_unit="1",
            vertical_direct_gravity_m_s2=(0.0, 2.0),
            model_scope="fixture",
        )
        self.assertIsNone(signal.vertical_direct_gravity_gradient_s2)
        self.assertIsNone(signal.peak_absolute_gravity_gradient_s2)


if __name__ == "__main__":
    unittest.main()
