"""Evidence-state tests for control and compute machine inventory."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class TestMachineInventory(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads((ROOT / "data/manifests/machines.json").read_text())

    def test_control_plane_is_inspected_and_has_no_gpu_claim(self) -> None:
        control = self.document["machines"][0]
        self.assertEqual(control["verification_status"], "locally-inspected")
        self.assertEqual(control["cpu"]["logical_cpus"], 1)
        self.assertIsNone(control["gpu"])
        self.assertFalse(control["uv_available"])
        self.assertFalse(control["docker_available"])

    def test_compute_plane_records_inspected_hardware_and_locked_runtime(self) -> None:
        compute = self.document["machines"][1]
        self.assertEqual(compute["verification_status"], "remotely-inspected")
        self.assertEqual(compute["cpu"]["logical_cpus"], 64)
        self.assertEqual(compute["gpu"]["model"], "NVIDIA RTX 5000 Ada Generation")
        self.assertEqual(compute["gpu"]["count"], 4)
        self.assertEqual(compute["driver"], "570.124.06")
        self.assertEqual(compute["python"], "3.12.12")
        self.assertIsNone(compute["locked_scientific_environment"]["torch"])

    def test_cross_machine_equivalence_is_not_claimed(self) -> None:
        regression = self.document["cross_machine_regression"]
        self.assertTrue(regression["status"].endswith("vultr-rerun-pending"))
        self.assertEqual(len(regression["required_experiments"]), 5)
        self.assertEqual(regression["autodl_registered_outputs_reproduced"], 5)


if __name__ == "__main__":
    unittest.main()
