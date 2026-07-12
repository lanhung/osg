"""Semantic-safety tests for scenario envelopes and probability priors."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.evaluation import (  # noqa: E402
    ParameterEnvelope,
    sample_parameter_design,
)


class TestParameterPriors(unittest.TestCase):
    def test_engineering_envelope_is_never_labelled_probability(self) -> None:
        envelope = ParameterEnvelope(
            name="distance_m",
            unit="m",
            lower=1_000.0,
            upper=1_000_000.0,
            scale="log",
            evidence_status="engineering_fixture",
            range_semantics="scenario_envelope",
            sources=("foundation configuration",),
        )
        design = sample_parameter_design([envelope], 8, random_seed=42)
        self.assertEqual(
            design.interpretation,
            "space_filling_scenario_design_not_probability_samples",
        )
        self.assertEqual(design, sample_parameter_design([envelope], 8, random_seed=42))

    def test_supported_probability_prior_retains_probability_label(self) -> None:
        envelope = ParameterEnvelope(
            name="amplitude_m",
            unit="m",
            lower=0.1,
            upper=1.0,
            scale="linear",
            evidence_status="literature_supported",
            range_semantics="probability_prior",
            sources=("doi:10.example/fixture",),
        )
        design = sample_parameter_design([envelope], 4, random_seed=7)
        self.assertEqual(design.interpretation, "probability_prior_samples")

    def test_unsupported_semantics_and_evidence_are_rejected(self) -> None:
        common = {
            "name": "x",
            "unit": "m",
            "lower": 1.0,
            "upper": 2.0,
            "scale": "linear",
        }
        with self.assertRaises(ValueError):
            ParameterEnvelope(
                **common,
                evidence_status="engineering_fixture",
                range_semantics="probability_prior",
            )
        with self.assertRaises(ValueError):
            ParameterEnvelope(
                **common,
                evidence_status="literature_supported",
                range_semantics="scenario_envelope",
            )


if __name__ == "__main__":
    unittest.main()
