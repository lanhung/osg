"""Run and checksum a registered deterministic experiment."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper", required=True, choices=("1", "2", "3"))
    parser.add_argument("--experiment", required=True)
    return parser.parse_args()


def _load_metadata(root: Path, paper: str, experiment: str) -> tuple[Path, dict]:
    experiment_dir = root / "experiments" / f"paper{paper}" / experiment
    metadata_path = experiment_dir / "metadata.json"
    if not metadata_path.is_file():
        raise ValueError(
            f"Unregistered experiment {experiment!r}: expected {metadata_path}. "
            "Refusing to run without versioned metadata."
        )
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("experiment_id") != experiment:
        raise ValueError("metadata experiment_id does not match requested experiment")
    if metadata.get("paper") != f"paper{paper}":
        raise ValueError("metadata paper does not match requested paper")
    return experiment_dir, metadata


def _resolve_inside_root(root: Path, relative_path: str) -> Path:
    candidate = (root / relative_path).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as error:
        raise ValueError(f"registered path escapes repository root: {relative_path}") from error
    return candidate


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        _experiment_dir, metadata = _load_metadata(root, args.paper, args.experiment)
        runner = _resolve_inside_root(root, metadata["runner"])
        config = _resolve_inside_root(root, metadata["config_file"])
        outputs = metadata["outputs"]
        if not isinstance(outputs, list) or len(outputs) == 0:
            raise ValueError("metadata outputs must be a non-empty list")
        if len(outputs) != 1:
            raise ValueError("current deterministic runner contract requires exactly one output")
        output = _resolve_inside_root(root, outputs[0]["path"])
        expected_sha256 = outputs[0]["sha256"]
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        raise SystemExit(str(error)) from error

    output.parent.mkdir(parents=True, exist_ok=True)
    command = [sys.executable, str(runner), "--config", str(config), "--output", str(output)]
    subprocess.run(command, cwd=root, check=True)
    actual_sha256 = _sha256(output)
    if actual_sha256 != expected_sha256:
        raise SystemExit(
            f"Output checksum mismatch for {output}: expected {expected_sha256}, "
            f"got {actual_sha256}"
        )
    print(
        json.dumps(
            {
                "experiment_id": metadata["experiment_id"],
                "output": str(output.relative_to(root)),
                "sha256": actual_sha256,
                "status": "reproduced",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
