"""Cross-platform canonical experiment-report value tests."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.evaluation import canonicalize_report_floats


class TestCanonicalReportFloats(unittest.TestCase):
    def test_recursively_rounds_only_floats(self) -> None:
        value = {
            "small": 9.664002073447226e-11,
            "large": [14833.731042260915, 3, True, "kept"],
        }
        self.assertEqual(
            canonicalize_report_floats(value, significant_digits=10),
            {
                "small": 9.664002073e-11,
                "large": [14833.73104, 3, True, "kept"],
            },
        )

    def test_rejects_invalid_precision_and_nonfinite_values(self) -> None:
        with self.assertRaises(ValueError):
            canonicalize_report_floats(1.0, significant_digits=0)
        with self.assertRaises(TypeError):
            canonicalize_report_floats(1.0, significant_digits=True)
        with self.assertRaises(ValueError):
            canonicalize_report_floats(float("nan"), significant_digits=10)


if __name__ == "__main__":
    unittest.main()
