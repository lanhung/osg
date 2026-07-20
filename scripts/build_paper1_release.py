"""Build every Paper 1 figure, audit and PDF from frozen registered metrics."""

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
FIGURES = ROOT / "reports/figures/paper1"
PAPER = ROOT / "papers/paper1_atlas"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command: list[str], *, cwd: Path = ROOT) -> dict:
    result = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "SOURCE_DATE_EPOCH": "1783900800",
            "FORCE_SOURCE_DATE": "1",
            "MPLCONFIGDIR": "/tmp/oceangravity-matplotlib",
            "TZ": "UTC",
        },
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--skip-pdf", action="store_true")
    parser.add_argument("--report", type=Path, default=ROOT / "reports/paper1_release_build.json")
    args = parser.parse_args()
    python = args.python
    records: list[dict] = []

    records.append(run([python, "scripts/validate_experiment_registry.py"]))
    records.append(
        run(
            [
                python,
                "scripts/audit_p1_literature_matrix.py",
                "--matrix",
                "docs/paper1_literature_matrix.csv",
                "--bibliography",
                "papers/paper1_atlas/references.bib",
                "--output",
                "reports/p1_literature_matrix_audit.json",
            ]
        )
    )

    # Preserve the renderer's four-figure submanifest separately from the
    # authoritative five-main-figure manuscript manifest.
    records.append(
        run(
            [
                python,
                "scripts/render_p1_production_figures.py",
                "--output-dir",
                str(FIGURES),
                "--curves",
                "data/manifests/instrument_noise_curves_reviewed_v2.json",
                "--manifest-path",
                str(FIGURES / "p1_production_renderer_manifest.json"),
            ]
        )
    )
    records.append(
        run(
            [
                python,
                "scripts/render_p1_frequency_requirements.py",
                "--metrics",
                "experiments/paper1/P1-E011-temporal-spectral-convergence/metrics.json",
                "--instrument-curves",
                "data/manifests/instrument_noise_curves_reviewed_v2.json",
                "--output-svg",
                str(FIGURES / "p1_frequency_requirements.svg"),
                "--output-png",
                str(FIGURES / "p1_frequency_requirements.png"),
            ]
        )
    )
    records.append(
        run(
            [
                python,
                "scripts/render_p1_conceptual_observables.py",
                "--output-svg",
                str(FIGURES / "p1_observable_framework.svg"),
                "--output-png",
                str(FIGURES / "p1_observable_framework.png"),
            ]
        )
    )
    records.append(
        run(
            [
                python,
                "scripts/render_p1_structure_validation.py",
                "--source-metrics",
                "experiments/paper1/P1-E005-helgoland-bsh-model/metrics.json",
                "--component-audit",
                "experiments/paper1/P1-E009-helgoland-component-audit/metrics.json",
                "--output-svg",
                str(FIGURES / "p1_structure_validation.svg"),
                "--output-png",
                str(FIGURES / "p1_structure_validation.png"),
            ]
        )
    )
    records.append(
        run(
            [
                python,
                "scripts/audit_p1_observable_ledger.py",
                "--root",
                ".",
                "--ledger",
                "data/manifests/paper1_observable_ledger.csv",
                "--figure-manifest",
                "papers/paper1_atlas/figure_manifest.json",
                "--output",
                "reports/p1_observable_ledger_audit.json",
            ]
        )
    )

    literature = json.loads((ROOT / "reports/p1_literature_matrix_audit.json").read_text())
    observable = json.loads((ROOT / "reports/p1_observable_ledger_audit.json").read_text())
    if (
        not all(
            literature[key]
            for key in (
                "minimum_reference_gate_passes",
                "full_text_gate_passes",
                "process_coverage_gate_passes",
            )
        )
        or literature["forbidden_placeholder_author_present"]
    ):
        raise RuntimeError("Paper 1 literature audit did not pass")
    if not observable["audit_passes"]:
        raise RuntimeError("Paper 1 observable audit did not pass")

    if not args.skip_pdf:
        for executable in ("pdflatex", "bibtex"):
            if shutil.which(executable) is None:
                raise RuntimeError(f"required executable not found: {executable}")
        latex_command = [
            "pdflatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "main.tex",
        ]
        records.append(run(latex_command, cwd=PAPER))
        records.append(run(["bibtex", "main"], cwd=PAPER))
        records.append(run(latex_command, cwd=PAPER))
        records.append(run(latex_command, cwd=PAPER))
        latex_log = (PAPER / "main.log").read_text(errors="replace")
        forbidden = ("There were undefined references", "Citation `", "Reference `")
        if any(marker in latex_log for marker in forbidden):
            raise RuntimeError("LaTeX log contains undefined citations or references")

    artifacts = [
        FIGURES / "p1_observable_framework.svg",
        FIGURES / "p1_observable_framework.png",
        FIGURES / "p1_frequency_coverage.svg",
        FIGURES / "p1_frequency_coverage.png",
        FIGURES / "p1_frequency_requirements.svg",
        FIGURES / "p1_frequency_requirements.png",
        FIGURES / "p1_distance_amplitude_envelopes.svg",
        FIGURES / "p1_distance_amplitude_envelopes.png",
        FIGURES / "p1_structure_validation.svg",
        FIGURES / "p1_structure_validation.png",
        ROOT / "reports/p1_literature_matrix_audit.json",
        ROOT / "reports/p1_observable_ledger_audit.json",
    ]
    if not args.skip_pdf:
        artifacts.append(PAPER / "main.pdf")
    payload = {
        "schema_version": 1,
        "workflow": "paper1-release",
        "uses_frozen_registered_metrics": [
            "P1-E005",
            "P1-E006",
            "P1-E008",
            "P1-E009",
            "P1-E010",
            "P1-E011",
        ],
        "commands": records,
        "artifacts": {
            str(path.relative_to(ROOT)): {"bytes": path.stat().st_size, "sha256": sha256(path)}
            for path in artifacts
        },
        "literature_audit_passes": True,
        "observable_audit_passes": True,
        "pdf_built": not args.skip_pdf,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
