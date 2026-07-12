"""Validate and dispatch a registered experiment reproduction request."""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper", required=True, choices=("1", "2", "3"))
    parser.add_argument("--experiment", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    experiment_dir = root / "experiments" / f"paper{args.paper}" / args.experiment
    metadata = experiment_dir / "metadata.yml"
    if not metadata.is_file():
        raise SystemExit(
            f"Unregistered experiment {args.experiment!r}: expected {metadata}. "
            "Refusing to run without versioned metadata."
        )
    raise SystemExit(
        f"Experiment metadata found at {metadata}, but no workflow dispatcher is registered yet."
    )


if __name__ == "__main__":
    main()

