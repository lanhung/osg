"""Validate registered experiment metadata, paths, and frozen checksums."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve_inside_root(root: Path, relative_path: str) -> Path:
    if not isinstance(relative_path, str) or not relative_path:
        raise ValueError("registered paths must be non-empty strings")
    candidate = (root / relative_path).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as error:
        raise ValueError(f"registered path escapes repository root: {relative_path}") from error
    return candidate


def validate_metadata_document(root: Path, metadata_path: Path) -> dict:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    required = {
        "schema_version",
        "experiment_id",
        "paper",
        "code_commit",
        "config_file",
        "config_file_sha256",
        "runner",
        "outputs",
        "environment",
        "machine",
        "result_class",
    }
    missing = sorted(required - metadata.keys())
    if missing:
        raise ValueError(f"missing required metadata fields: {', '.join(missing)}")
    if metadata["schema_version"] != 1:
        raise ValueError("unsupported experiment metadata schema version")
    experiment_id = metadata["experiment_id"]
    if not isinstance(experiment_id, str) or metadata_path.parent.name != experiment_id:
        raise ValueError("experiment_id must match the metadata parent directory")
    paper = metadata["paper"]
    if paper not in {"paper1", "paper2", "paper3"}:
        raise ValueError("paper must be paper1, paper2, or paper3")
    if metadata_path.parent.parent.name != paper:
        raise ValueError("paper must match the experiment directory")
    if not isinstance(metadata["code_commit"], str) or not COMMIT_PATTERN.fullmatch(
        metadata["code_commit"]
    ):
        raise ValueError("code_commit must be a full lowercase Git SHA-1")
    for field in ("machine", "result_class"):
        if not isinstance(metadata[field], str) or not metadata[field].strip():
            raise ValueError(f"{field} must be a non-empty string")
    if not isinstance(metadata["environment"], dict):
        raise ValueError("environment must be an object")

    config = resolve_inside_root(root, metadata["config_file"])
    runner = resolve_inside_root(root, metadata["runner"])
    if not config.is_file() or not runner.is_file():
        raise ValueError("registered config_file and runner must exist")
    if sha256_file(config) != metadata["config_file_sha256"]:
        raise ValueError("config_file_sha256 does not match the registered config")
    if metadata.get("data_manifest") is not None:
        manifest = resolve_inside_root(root, metadata["data_manifest"])
        if not manifest.is_file():
            raise ValueError("registered data_manifest must exist")

    outputs = metadata["outputs"]
    if not isinstance(outputs, list) or not outputs:
        raise ValueError("outputs must be a non-empty list")
    seen_paths: set[str] = set()
    for output in outputs:
        if not isinstance(output, dict) or set(output) != {"path", "sha256"}:
            raise ValueError("each output must contain exactly path and sha256")
        if output["path"] in seen_paths:
            raise ValueError("output paths must be unique")
        seen_paths.add(output["path"])
        path = resolve_inside_root(root, output["path"])
        if not path.is_file():
            raise ValueError(f"registered output does not exist: {output['path']}")
        if sha256_file(path) != output["sha256"]:
            raise ValueError(f"output checksum mismatch: {output['path']}")
    return metadata


def validate_registry(root: Path) -> list[dict]:
    metadata_paths = sorted((root / "experiments").glob("paper*/**/metadata.json"))
    if not metadata_paths:
        raise ValueError("experiment registry contains no metadata documents")
    return [validate_metadata_document(root, path) for path in metadata_paths]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    return parser.parse_args()


def main() -> int:
    root = parse_args().root.resolve()
    documents = validate_registry(root)
    print(
        json.dumps(
            {
                "experiments": [document["experiment_id"] for document in documents],
                "registered_count": len(documents),
                "status": "valid",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
