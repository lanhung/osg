"""Determinism, stratification, transform, and quantile tests."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.evaluation import (  # noqa: E402
    ParameterRange,
    latin_hypercube,
    quantile,
    summarize_ensemble,
)


class TestLatinHypercube(unittest.TestCase):
    def test_same_seed_is_identical_and_different_seed_changes_samples(self) -> None:
        parameters = [ParameterRange("x", 0.0, 1.0), ParameterRange("y", 1.0, 10.0, "log")]
        first = latin_hypercube(parameters, 16, random_seed=42)
        second = latin_hypercube(parameters, 16, random_seed=42)
        third = latin_hypercube(parameters, 16, random_seed=43)
        self.assertEqual(first, second)
        self.assertNotEqual(first, third)

    def test_every_linear_dimension_occupies_each_stratum_once(self) -> None:
        sample_count = 32
        samples = latin_hypercube(
            [ParameterRange("x", -2.0, 6.0), ParameterRange("y", 10.0, 20.0)],
            sample_count,
            random_seed=20260712,
        )
        for name, lower, upper in (("x", -2.0, 6.0), ("y", 10.0, 20.0)):
            strata = sorted(
                math.floor((sample[name] - lower) / (upper - lower) * sample_count)
                for sample in samples
            )
            self.assertEqual(strata, list(range(sample_count)))

    def test_log_dimension_is_stratified_in_log_space(self) -> None:
        sample_count = 20
        lower = 1.0e-3
        upper = 1.0e2
        samples = latin_hypercube(
            [ParameterRange("frequency", lower, upper, "log")],
            sample_count,
            random_seed=7,
        )
        strata = sorted(
            math.floor(
                math.log(sample["frequency"] / lower)
                / math.log(upper / lower)
                * sample_count
            )
            for sample in samples
        )
        self.assertEqual(strata, list(range(sample_count)))

    def test_quantile_type7_known_values(self) -> None:
        values = [0.0, 10.0, 20.0, 30.0, 40.0]
        self.assertEqual(quantile(values, 0.0), 0.0)
        self.assertEqual(quantile(values, 0.5), 20.0)
        self.assertEqual(quantile(values, 0.95), 38.0)
        self.assertEqual(quantile(values, 1.0), 40.0)

    def test_ensemble_summary_has_expected_quantiles(self) -> None:
        summary = summarize_ensemble(
            [{"a": 0.0, "b": 10.0}, {"a": 10.0, "b": 20.0}, {"a": 20.0, "b": 30.0}]
        )
        self.assertEqual(summary["a"], {"q05": 1.0, "q50": 10.0, "q95": 19.0})
        self.assertEqual(summary["b"], {"q05": 11.0, "q50": 20.0, "q95": 29.0})

    def test_invalid_ranges_names_counts_and_metrics_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ParameterRange("x", 0.0, 0.0)
        with self.assertRaises(ValueError):
            ParameterRange("x", 0.0, 1.0, "log")
        with self.assertRaises(ValueError):
            latin_hypercube([ParameterRange("x", 0.0, 1.0)], 0, random_seed=1)
        with self.assertRaises(ValueError):
            latin_hypercube(
                [ParameterRange("x", 0.0, 1.0), ParameterRange("x", 1.0, 2.0)],
                2,
                random_seed=1,
            )
        with self.assertRaises(ValueError):
            summarize_ensemble([{"a": 1.0}, {"b": 2.0}])


if __name__ == "__main__":
    unittest.main()

