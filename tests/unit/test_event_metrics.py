"""Paper 2 event attribution metric tests."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.evaluation import evaluate_event_model_metrics  # noqa: E402


class TestEventMetrics(unittest.TestCase):
    def test_perfect_model_has_closed_metrics(self) -> None:
        metrics = evaluate_event_model_metrics(
            (0.0, 60.0, 120.0), (0.0, -2.0, 1.0), (0.0, -2.0, 1.0)
        )
        self.assertEqual(metrics.bias_m_s2, 0.0)
        self.assertEqual(metrics.rmse_m_s2, 0.0)
        self.assertAlmostEqual(metrics.pearson_correlation, 1.0)
        self.assertEqual(metrics.explained_variance_fraction, 1.0)
        self.assertEqual(metrics.observed_peak_m_s2, -2.0)
        self.assertEqual(metrics.peak_amplitude_error_m_s2, 0.0)
        self.assertEqual(metrics.peak_time_error_s, 0.0)

    def test_peak_is_signed_absolute_and_time_error_is_modeled_minus_observed(self) -> None:
        metrics = evaluate_event_model_metrics(
            (0.0, 10.0, 20.0, 30.0),
            (0.0, -5.0, 4.0, 0.0),
            (0.0, -1.0, -6.0, 0.0),
        )
        self.assertEqual(metrics.observed_peak_m_s2, -5.0)
        self.assertEqual(metrics.modeled_peak_m_s2, -6.0)
        self.assertEqual(metrics.peak_amplitude_error_m_s2, -1.0)
        self.assertEqual(metrics.peak_time_error_s, 10.0)

    def test_mask_changes_metrics_without_changing_input(self) -> None:
        observed = (0.0, 100.0, 2.0, 3.0)
        modeled = (0.0, -100.0, 2.0, 3.0)
        metrics = evaluate_event_model_metrics(
            (0.0, 1.0, 2.0, 3.0),
            observed,
            modeled,
            inclusion_mask=(True, False, True, True),
        )
        self.assertEqual(metrics.included_sample_count, 3)
        self.assertEqual(metrics.rmse_m_s2, 0.0)
        self.assertEqual(observed[1], 100.0)

    def test_constant_series_and_invalid_inputs_are_explicit(self) -> None:
        metrics = evaluate_event_model_metrics(
            (0.0, 1.0), (2.0, 2.0), (3.0, 3.0)
        )
        self.assertIsNone(metrics.pearson_correlation)
        self.assertIsNone(metrics.explained_variance_fraction)
        with self.assertRaises(ValueError):
            evaluate_event_model_metrics(
                (0.0, 1.0),
                (1.0, 2.0),
                (1.0, 2.0),
                inclusion_mask=(True, False),
            )


if __name__ == "__main__":
    unittest.main()
