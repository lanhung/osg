"""Validate and reproduce every registered deterministic experiment."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from validate_experiment_registry import validate_registry


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    documents = validate_registry(root)
    for metadata in documents:
        paper_number = metadata["paper"].removeprefix("paper")
        subprocess.run(
            [
                sys.executable,
                str(root / "scripts" / "reproduce.py"),
                "--paper",
                paper_number,
                "--experiment",
                metadata["experiment_id"],
            ],
            cwd=root,
            check=True,
        )
    validate_registry(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
