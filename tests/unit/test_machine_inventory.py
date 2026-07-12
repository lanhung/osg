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

    def test_compute_plane_unknowns_remain_null(self) -> None:
        compute = self.document["machines"][1]
        self.assertEqual(compute["verification_status"], "user-described-not-inspected")
        self.assertEqual(compute["gpu"]["model"], "NVIDIA A5000")
        self.assertIsNone(compute["gpu"]["count"])
        self.assertIsNone(compute["cuda"])

    def test_cross_machine_equivalence_is_not_claimed(self) -> None:
        regression = self.document["cross_machine_regression"]
        self.assertTrue(regression["status"].startswith("pending"))
        self.assertEqual(len(regression["required_experiments"]), 4)


if __name__ == "__main__":
    unittest.main()
