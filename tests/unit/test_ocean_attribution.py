"""Leakage-safe Paper 2 ocean attribution tests."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.evaluation import (
    fit_ocean_attribution_coefficient,
    predict_heldout_ocean_attribution,
)


class TestOceanAttribution(unittest.TestCase):
    def test_fit_recovers_intercept_and_coefficient_from_training_events(self) -> None:
        baseline = (10.0,) * 8
        ocean = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 100.0, 200.0)
        events = ("T1",) * 3 + ("T2",) * 3 + ("H1",) * 2
        observed = tuple(
            base + 2.0 + 3.0 * ocean_value
            for base, ocean_value in zip(baseline, ocean, strict=True)
        )
        fit = fit_ocean_attribution_coefficient(
            observed,
            baseline,
            ocean,
            events,
            training_event_ids=("T2", "T1"),
        )
        self.assertAlmostEqual(fit.intercept_m_s2, 2.0)
        self.assertAlmostEqual(fit.ocean_coefficient, 3.0)
        self.assertAlmostEqual(fit.ocean_coefficient_standard_error, 0.0)
        self.assertEqual(fit.training_event_ids, ("T1", "T2"))
        prediction = predict_heldout_ocean_attribution(
            fit, (10.0, 10.0), (100.0, 200.0), event_id="H1"
        )
        self.assertEqual(prediction, observed[-2:])

    def test_training_event_cannot_be_called_heldout(self) -> None:
        fit = fit_ocean_attribution_coefficient(
            (0.0, 1.0, 2.0),
            (0.0, 0.0, 0.0),
            (0.0, 1.0, 2.0),
            ("T1", "T1", "T1"),
            training_event_ids=("T1",),
        )
        with self.assertRaisesRegex(ValueError, "not held out"):
            predict_heldout_ocean_attribution(fit, (0.0,), (1.0,), event_id="T1")

    def test_mask_and_training_identity_control_selected_samples(self) -> None:
        fit = fit_ocean_attribution_coefficient(
            (1.0, 3.0, 5.0, 999.0, 999.0),
            (0.0,) * 5,
            (0.0, 1.0, 2.0, 3.0, 4.0),
            ("T1", "T1", "T1", "H1", "T1"),
            training_event_ids=("T1",),
            inclusion_mask=(True, True, True, True, False),
        )
        self.assertEqual(fit.included_sample_count, 3)
        self.assertAlmostEqual(fit.intercept_m_s2, 1.0)
        self.assertAlmostEqual(fit.ocean_coefficient, 2.0)

    def test_zero_variance_and_unknown_training_event_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "zero variance"):
            fit_ocean_attribution_coefficient(
                (1.0, 2.0, 3.0),
                (0.0, 0.0, 0.0),
                (1.0, 1.0, 1.0),
                ("T1", "T1", "T1"),
                training_event_ids=("T1",),
            )
        with self.assertRaisesRegex(ValueError, "no samples"):
            fit_ocean_attribution_coefficient(
                (1.0, 2.0, 3.0),
                (0.0, 0.0, 0.0),
                (1.0, 2.0, 3.0),
                ("T1", "T1", "T1"),
                training_event_ids=("missing",),
            )


if __name__ == "__main__":
    unittest.main()
