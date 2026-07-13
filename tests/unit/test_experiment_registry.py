"""Validation tests for the immutable experiment registry contract."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_experiment_registry import validate_registry  # noqa: E402


class TestExperimentRegistry(unittest.TestCase):
    def test_repository_registry_is_valid_and_complete(self) -> None:
        documents = validate_registry(ROOT)
        self.assertEqual(
            [document["experiment_id"] for document in documents],
            [
                "P1-E001-foundation",
                "P1-E002-detectability-foundation",
                "P1-E003-gradient-detectability-foundation",
                "P1-E004-distance-attenuation-foundation",
                "P1-E005-helgoland-bsh-model",
                "P1-E006-evidence-bounded-atlas",
                "P1-E007-structural-variant-closure",
                "P1-E008-frequency-coverage-requirements",
                "P1-E009-helgoland-component-audit",
                "P1-E010-independent-review-sensitivity",
                "P2-E001-nonrestricted-readiness",
                "P2-E002-cmems-effect-ownership",
                "P3-E001-physical-baseline-foundation",
                "P3-E002-archive-network-design",
                "P3-E003-seasonal-noise-stage1",
            ],
        )


if __name__ == "__main__":
    unittest.main()
