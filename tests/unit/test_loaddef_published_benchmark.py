"""Published LoadDef table parser tests."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "evaluate_loaddef_published_benchmark",
    ROOT / "scripts/evaluate_loaddef_published_benchmark.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class TestLoadDefPublishedBenchmark(unittest.TestCase):
    def test_numeric_rows_ignore_headers_and_preserve_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "table.txt"
            path.write_text("header words\n0.10000 -1.0000e+00 2.0\n", encoding="utf-8")
            self.assertEqual(
                MODULE.numeric_token_rows(path, 3),
                {"0.10000": ("0.10000", "-1.0000e+00", "2.0")},
            )

    def test_duplicate_numeric_keys_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "table.txt"
            path.write_text("1 2\n1 3\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate numeric row key"):
                MODULE.numeric_token_rows(path, 2)


if __name__ == "__main__":
    unittest.main()
