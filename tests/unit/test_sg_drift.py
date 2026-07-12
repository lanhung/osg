"""Explicit SG drift correction tests."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.signal_processing import (  # noqa: E402
    InstrumentDriftModel,
    apply_instrument_drift_model,
)


def _model(**changes):
    values = {
        "model_id": "quiet-window-drift-v1",
        "reference_time_utc": "2024-01-02T00:00:00Z",
        "valid_start_utc": "2024-01-01T00:00:00Z",
        "valid_end_utc": "2024-01-05T00:00:00Z",
        "linear_rate_m_s2_per_s": 2.0e-12,
        "linear_rate_standard_uncertainty_m_s2_per_s": 1.0e-13,
        "quadratic_rate_m_s2_per_s2": 4.0e-17,
        "quadratic_rate_standard_uncertainty_m_s2_per_s2": 2.0e-18,
        "source": "unit-test fixture",
        "rationale": "declared outside event window",
        "fit_data_role": "quiet_windows_only",
    }
    values.update(changes)
    return InstrumentDriftModel(**values)


class TestSgDrift(unittest.TestCase):
    def test_linear_quadratic_drift_sign_and_uncertainty(self) -> None:
        times = (
            "2024-01-01T00:00:00Z",
            "2024-01-02T00:00:00Z",
            "2024-01-03T00:00:00Z",
        )
        model = _model()
        result = apply_instrument_drift_model(times, (1.0, 1.0, 1.0), model)
        day = 86400.0
        expected_early = -model.linear_rate_m_s2_per_s * day + 0.5 * model.quadratic_rate_m_s2_per_s2 * day**2
        expected_late = model.linear_rate_m_s2_per_s * day + 0.5 * model.quadratic_rate_m_s2_per_s2 * day**2
        self.assertAlmostEqual(result.removed_drift_m_s2[0], expected_early)
        self.assertEqual(result.removed_drift_m_s2[1], 0.0)
        self.assertAlmostEqual(result.removed_drift_m_s2[2], expected_late)
        expected_uncertainty = math.hypot(
            day * model.linear_rate_standard_uncertainty_m_s2_per_s,
            0.5 * day**2 * model.quadratic_rate_standard_uncertainty_m_s2_per_s2,
        )
        self.assertAlmostEqual(
            result.removed_drift_standard_uncertainty_m_s2[2], expected_uncertainty
        )
        self.assertAlmostEqual(result.corrected_m_s2[2], 1.0 - expected_late)

    def test_validity_and_time_order_prevent_extrapolation(self) -> None:
        model = _model()
        with self.assertRaisesRegex(ValueError, "extrapolate"):
            apply_instrument_drift_model(
                ("2024-01-05T00:00:00Z",), (1.0,), model
            )
        with self.assertRaisesRegex(ValueError, "strictly increasing"):
            apply_instrument_drift_model(
                ("2024-01-02T00:00:00Z", "2024-01-01T00:00:00Z"),
                (1.0, 1.0),
                model,
            )

    def test_model_rejects_event_fit_role_and_bad_reference(self) -> None:
        with self.assertRaises(ValueError):
            _model(fit_data_role="event_window")
        with self.assertRaises(ValueError):
            _model(reference_time_utc="2025-01-01T00:00:00Z")


if __name__ == "__main__":
    unittest.main()
