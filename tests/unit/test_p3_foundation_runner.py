"""Claim boundaries for the registered Paper 3 foundation runner."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "run_p3_foundation", ROOT / "scripts/run_p3_physical_baseline_foundation.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class TestP3FoundationRunner(unittest.TestCase):
    def test_fixture_never_claims_scientific_readiness(self) -> None:
        config = json.loads((ROOT / "configs/paper3/physical_baseline_foundation.json").read_text())
        result = MODULE.run(config)
        self.assertFalse(result["scientific_claim_ready"])
        self.assertFalse(
            result["single_station_energy_audit"]["quiet_false_positive_audit"][
                "rate_resolution_sufficient"
            ]
        )
        self.assertEqual(
            result["discrete_source_inversion"]["best_scenario_id"],
            "fixture_mw86_central",
        )


if __name__ == "__main__":
    unittest.main()
