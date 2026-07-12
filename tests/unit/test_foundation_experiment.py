"""Offline determinism and schema tests for the Paper 1 foundation experiment."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from run_p1_foundation import build_process_signals, run  # noqa: E402


class TestFoundationExperiment(unittest.TestCase):
    def test_result_is_deterministic_and_contains_all_processes(self) -> None:
        config = json.loads(
            (ROOT / "configs/paper1/foundation_reference.json").read_text(encoding="utf-8")
        )
        first = run(config)
        second = run(config)
        self.assertEqual(first, second)
        self.assertEqual(
            set(first["metrics"]),
            {
                "tide",
                "storm_surge",
                "eddy_surface",
                "internal_wave_dipole",
                "tsunami_packet",
                "submarine_landslide",
            },
        )
        for process_metrics in first["metrics"].values():
            self.assertGreater(process_metrics["peak_absolute_direct_gravity_m_s2"], 0.0)
            self.assertGreater(process_metrics["dominant_nonzero_frequency_hz"], 0.0)
        self.assertEqual(first["result_class"], "engineering_reference_not_cited_physical_prior")

    def test_json_round_trip_is_stable(self) -> None:
        config = json.loads(
            (ROOT / "configs/paper1/foundation_reference.json").read_text(encoding="utf-8")
        )
        result = run(config)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "metrics.json"
            path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
            self.assertEqual(json.loads(path.read_text()), result)

    def test_all_six_processes_now_expose_vertical_gradient(self) -> None:
        config = json.loads(
            (ROOT / "configs/paper1/foundation_reference.json").read_text(encoding="utf-8")
        )
        built = build_process_signals(config)
        self.assertEqual(len(built), 6)
        for signal, _, _ in built.values():
            self.assertIsNotNone(signal.vertical_direct_gravity_gradient_s2)
            self.assertGreater(signal.peak_absolute_gravity_gradient_s2, 0.0)


if __name__ == "__main__":
    unittest.main()
