"""Compare LoadDef outputs with the published Martens et al. (2019) data tables."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def numeric_token_rows(path: Path, expected_columns: int) -> dict[str, tuple[str, ...]]:
    rows: dict[str, tuple[str, ...]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        fields = tuple(line.split())
        if len(fields) != expected_columns:
            continue
        try:
            tuple(float(value) for value in fields)
        except ValueError:
            continue
        key = fields[0]
        if key in rows:
            raise ValueError(f"duplicate numeric row key {key!r} in {path}")
        rows[key] = fields
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--published-dir", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    benchmark = config["published_benchmark"]
    for record in benchmark["files"].values():
        path = args.published_dir / record["name"]
        if not path.is_file() or _sha256(path) != record["sha256"]:
            raise SystemExit(f"published benchmark checksum failure: {path}")

    comparisons = []
    published_lln = numeric_token_rows(args.published_dir / benchmark["files"]["LLN"]["name"], 7)
    generated_lln = numeric_token_rows(args.source_root / "output/Love_Numbers/LLN/lln_PREM.txt", 7)
    comparisons.append(("LLN", published_lln, generated_lln))
    for frame in ("CE", "CM", "CF"):
        published = numeric_token_rows(args.published_dir / benchmark["files"][frame]["name"], 12)
        generated = numeric_token_rows(
            args.source_root / f"output/Greens_Functions/{frame.lower()}_PREM_audit_angles.txt",
            12,
        )
        comparisons.append((frame, published, generated))

    results = {}
    total_mismatches = 0
    provider_mismatches = 0
    provider_columns = tuple(
        benchmark["project_provider_comparison_rule"]["green_function_zero_based_columns"]
    )
    for name, published, generated in comparisons:
        missing = sorted(set(generated) - set(published), key=float)
        mismatches = sorted(
            (
                key
                for key in generated.keys() & published.keys()
                if generated[key] != published[key]
            ),
            key=float,
        )
        total_mismatches += len(missing) + len(mismatches)
        provider_mismatch_keys = []
        if name != "LLN":
            provider_mismatch_keys = sorted(
                (
                    key
                    for key in generated.keys() & published.keys()
                    if tuple(generated[key][index] for index in provider_columns)
                    != tuple(published[key][index] for index in provider_columns)
                ),
                key=float,
            )
            provider_mismatches += len(missing) + len(provider_mismatch_keys)
        results[name] = {
            "generated_rows_compared": len(generated),
            "published_rows_available": len(published),
            "missing_published_keys": missing,
            "numeric_token_mismatch_keys": mismatches,
            "project_provider_mismatch_keys": provider_mismatch_keys,
        }

    output = {
        "schema_version": 1,
        "benchmark_id": benchmark["id"],
        "comparison_rule": benchmark["comparison_rule"],
        "total_mismatches": total_mismatches,
        "project_provider_mismatches": provider_mismatches,
        "comparisons": results,
        "strict_all_columns_status": "passed" if total_mismatches == 0 else "failed",
        "project_provider_status": "passed" if provider_mismatches == 0 else "failed",
        "status": "passed" if provider_mismatches == 0 else "failed",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if provider_mismatches == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
