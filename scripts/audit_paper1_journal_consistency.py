"""Audit Paper 1 journal numbers and claim boundaries against registered artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(root: Path) -> dict:
    main = (root / "papers/paper1_atlas/main.tex").read_text()
    supplement = (root / "papers/paper1_journal_of_geodesy/supplementary.tex").read_text()
    e006 = json.loads(
        (root / "experiments/paper1/P1-E006-evidence-bounded-atlas/metrics.json").read_text()
    )
    e011 = json.loads(
        (
            root
            / "experiments/paper1/P1-E011-temporal-spectral-convergence/metrics.json"
        ).read_text()
    )
    instruments = json.loads(
        (root / "data/manifests/instrument_noise_curves_reviewed_v2.json").read_text()
    )
    figure_manifest = json.loads(
        (root / "papers/paper1_atlas/figure_manifest.json").read_text()
    )

    counts = e006["process_record_counts"]
    count_checks = {
        "e006_record_count_is_1446": e006["record_count"] == 1446,
        "e011_record_count_is_1446": e011["baseline_audit"]["record_count"] == 1446,
        "e011_record_array_has_1446_rows": len(e011["records"]) == 1446,
        "process_counts_sum_to_1446": sum(counts.values()) == 1446,
    }
    decision = e011["decision"]
    decision_checks = {
        "dense_pass_count_is_zero": decision["dense_90pct_curve_coverage_pass_total"] == 0,
        "zero_classification_is_stable": decision[
            "zero_of_1446_classification_conclusion_stable"
        ],
        "grid_medians_converged": decision["dense_grid_process_medians_converged"],
        "cadence_medians_converged": decision[
            "representative_cadence_process_medians_converged"
        ],
        "window_stable_processes_exact": set(decision["window_stable_processes"])
        == {"tide", "internal_wave"},
        "window_limited_processes_exact": set(decision["window_limited_processes"])
        == {"mesoscale_eddy", "storm_surge", "tsunami", "submarine_landslide"},
    }
    expected_main_fragments = (
        "0-of-1,446",
        "$2.157$--$2.216\\times10^{-5}$",
        "$1.817$--$2.101\\times10^{-5}$",
        "$1.407$--$2.793\\times10^{-8}$",
        "$7.837\\times10^{-7}$--$3.488\\times10^{-6}$",
        "$5.990$--$9.903\\times10^{-5}$",
        "$7.764\\times10^{-6}$--$1.846\\times10^{-5}$",
        "model-scale consistency",
        "window limited",
        "universal process constants",
    )
    forbidden_main_fragments = (
        "$3.89\\times10^{-8}$",
        "$7.72\\times10^{-7}$",
        "$1.10\\times10^{-5}$",
        "$2.15\\times10^{-5}$",
        "$4.92\\times10^{-5}$",
        "$2.63\\times10^{-4}$",
        "independent validation of the observations",
        "instruments cannot detect",
    )
    manuscript_checks = {
        "required_revised_fragments_present": all(
            fragment in main for fragment in expected_main_fragments
        ),
        "old_headline_values_absent_from_main": not any(
            fragment in main for fragment in forbidden_main_fragments
        ),
        "native_grid_table_is_historical": (
            "historical P1-E008 result" in supplement
            and "superseded for interpretation" in supplement
        ),
    }

    curve_edges = {
        curve["instrument_id"]: curve["frequencies_hz"][0]
        for curve in instruments["curves"]
    }
    instrument_checks = {
        "igrav_low_edge_is_1e_3": curve_edges.get(
            "igrav_quiet_j9_self_noise_anchor"
        )
        == 1e-3,
        "aqg_low_edge_is_5e_4": curve_edges.get("aqg_a01_field_short_term_anchor")
        == 5e-4,
        "fg5_low_edge_is_5e_4": curve_edges.get("fg5_228_short_term_anchor") == 5e-4,
        "figure_manifest_registers_e011": (
            "P1-E011-temporal-spectral-convergence" in figure_manifest["registered_inputs"]
        ),
        "all_figure_checksums_match": all(
            _sha256(root / figure["path"]) == figure["sha256"]
            for figure in figure_manifest["figures"]
        ),
    }
    groups = {
        "count_checks": count_checks,
        "decision_checks": decision_checks,
        "manuscript_checks": manuscript_checks,
        "instrument_and_figure_checks": instrument_checks,
    }
    failures = [
        f"{group}.{name}"
        for group, checks in groups.items()
        for name, passed in checks.items()
        if not passed
    ]
    return {
        "schema_version": 1,
        **groups,
        "failures": failures,
        "audit_passes": not failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "reports/paper1_journal_consistency_audit.json",
    )
    args = parser.parse_args()
    result = audit(args.root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if not result["audit_passes"]:
        raise SystemExit(
            "Paper 1 journal consistency audit failed: " + ", ".join(result["failures"])
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
