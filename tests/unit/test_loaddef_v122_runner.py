"""Input-contract tests for the external LoadDef v1.2.2 runner."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "run_loaddef_v122", ROOT / "scripts/run_loaddef_v122.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class TestLoadDefV122Runner(unittest.TestCase):
    def test_repository_config_has_frozen_source_and_production_degrees(self) -> None:
        config = json.loads(
            (ROOT / "configs/paper1/loaddef_v1.2.2_prem.json").read_text(encoding="utf-8")
        )
        self.assertEqual(config["source"]["version"], "1.2.2")
        self.assertEqual(len(config["source"]["tag_commit"]), 40)
        self.assertEqual(len(config["source"]["archive_sha256"]), 64)
        self.assertEqual(config["production"]["startn"], 0)
        self.assertEqual(config["production"]["stopn"], 10000)
        self.assertTrue(config["acceptance"]["published_benchmark_required_before_scientific_use"])

    def test_missing_external_artifacts_are_rejected(self) -> None:
        config = json.loads(
            (ROOT / "configs/paper1/loaddef_v1.2.2_prem.json").read_text(encoding="utf-8")
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(ValueError, "source archive is missing"):
                MODULE.validate_inputs(config, root / "source", root / "missing.tar.gz")


if __name__ == "__main__":
    unittest.main()
