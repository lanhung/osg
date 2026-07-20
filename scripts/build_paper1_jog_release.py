"""Build and audit the actual Paper 1 Journal of Geodesy submission package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "papers/paper1_journal_of_geodesy"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run(command: list[str], *, cwd: Path = ROOT) -> dict:
    result = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        env={**os.environ, "TZ": "UTC", "MPLCONFIGDIR": "/tmp/oceangravity-matplotlib"},
    )
    record = {
        "command": command,
        "cwd": str(cwd.relative_to(ROOT) if cwd != ROOT else "."),
        "returncode": result.returncode,
        "stdout_tail": result.stdout[-2000:],
        "stderr_tail": result.stderr[-2000:],
    }
    if result.returncode:
        raise RuntimeError(json.dumps(record, indent=2))
    return record


def _validate_submission_metadata(*, require_release: bool = True) -> dict:
    path = PAPER / "submission_metadata.json"
    metadata = json.loads(path.read_text())
    if require_release and metadata.get("status") != "complete_verified":
        raise RuntimeError("submission metadata is not complete and verified")
    if not metadata.get("affiliations"):
        raise RuntimeError("at least one verified affiliation is required")
    if not metadata.get("corresponding_author_email"):
        raise RuntimeError("corresponding-author email is required")
    if require_release:
        doi = metadata.get("archival_doi")
        if not isinstance(doi, str) or not doi.startswith("10."):
            raise RuntimeError("a finalized archival DOI is required")
        for field in (
            "author_contribution_statement",
            "funding_statement",
            "competing_interests_statement",
            "all_author_approval_date",
        ):
            if not isinstance(metadata.get(field), str) or not metadata[field].strip():
                raise RuntimeError(f"verified release metadata field is required: {field}")
    for author in metadata["authors_in_order"]:
        if not author["affiliation_ids"] or author["corresponding"] is None:
            raise RuntimeError("every author needs affiliations and corresponding-author status")
    return metadata


def _validate_e011() -> Path:
    experiment = ROOT / "experiments/paper1/P1-E011-temporal-spectral-convergence"
    metadata_path = experiment / "metadata.json"
    if not metadata_path.is_file():
        raise RuntimeError("P1-E011 finalized metadata is required")
    metadata = json.loads(metadata_path.read_text())
    output = ROOT / metadata["outputs"][0]["path"]
    if _sha256(output) != metadata["outputs"][0]["sha256"]:
        raise RuntimeError("P1-E011 output checksum does not match metadata")
    return output


def _validate_figure_manifest() -> None:
    manifest_path = ROOT / "papers/paper1_atlas/figure_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    if "P1-E011-temporal-spectral-convergence" not in manifest["registered_inputs"]:
        raise RuntimeError("figure manifest does not register P1-E011")
    for figure in manifest["figures"]:
        path = ROOT / figure["path"]
        if not path.is_file() or _sha256(path) != figure["sha256"]:
            raise RuntimeError(f"figure checksum mismatch: {figure['path']}")


def _scan_sources() -> None:
    forbidden = (
        "Journal of Geodesy submission draft",
        "permanent archival DOI should be inserted",
        "[PENDING",
        "?Zhang",
    )
    for path in (
        PAPER / "main.tex",
        PAPER / "supplementary.tex",
        ROOT / "papers/paper1_atlas/main.tex",
        ROOT / "papers/paper1_atlas/references.bib",
    ):
        text = path.read_text(errors="replace")
        for marker in forbidden:
            if marker in text:
                raise RuntimeError(f"forbidden draft marker {marker!r} in {path}")


def _compile(name: str, records: list[dict]) -> None:
    latex = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", f"{name}.tex"]
    records.append(_run(latex, cwd=PAPER))
    if name == "main":
        records.append(_run(["bibtex", name], cwd=PAPER))
    records.append(_run(latex, cwd=PAPER))
    records.append(_run(latex, cwd=PAPER))
    log = (PAPER / f"{name}.log").read_text(errors="replace")
    markers = (
        "There were undefined references",
        "Citation `",
        "Reference `",
        "undefined citations",
        "Rerun to get cross-references right",
    )
    if any(marker in log for marker in markers):
        raise RuntimeError(f"{name}.log contains unresolved citations or references")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument(
        "--candidate-audit",
        action="store_true",
        help="compile and audit before DOI/declaration approval without authorizing release",
    )
    parser.add_argument(
        "--report", type=Path, default=ROOT / "reports/paper1_jog_release_build.json"
    )
    args = parser.parse_args()
    metadata = _validate_submission_metadata(require_release=not args.candidate_audit)
    e011_output = _validate_e011()
    _scan_sources()
    records = [
        _run(
            [
                args.python,
                "scripts/build_paper1_release.py",
                "--python",
                args.python,
                "--skip-pdf",
            ]
        ),
        _run([args.python, "scripts/validate_experiment_registry.py"]),
        _run([args.python, "scripts/export_paper1_journal_tables.py"]),
    ]
    _validate_figure_manifest()
    for executable in ("pdflatex", "bibtex"):
        if shutil.which(executable) is None:
            raise RuntimeError(f"required executable not found: {executable}")
    _compile("main", records)
    _compile("supplementary", records)
    artifacts = [
        PAPER / "main.pdf",
        PAPER / "supplementary.pdf",
        *sorted((PAPER / "generated").glob("*.tex")),
        e011_output,
    ]
    payload = {
        "schema_version": 1,
        "workflow": "paper1-jog-release",
        "release_tag": metadata["release_tag"],
        "archival_doi": metadata["archival_doi"],
        "release_authorized": not args.candidate_audit,
        "commands": records,
        "artifacts": {
            str(path.relative_to(ROOT)): {"bytes": path.stat().st_size, "sha256": _sha256(path)}
            for path in artifacts
        },
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
