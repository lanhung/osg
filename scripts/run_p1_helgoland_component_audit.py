"""Decompose the registered Helgoland model series without redefining observables."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np


def _component_metrics(gravity: np.ndarray, height: np.ndarray) -> dict:
    centered_height = height - height.mean()
    centered_gravity = gravity - gravity.mean()
    slope = -float(centered_height @ centered_gravity) / float(centered_height @ centered_height)
    return {
        "paper_convention_ratio_nm_s2_per_mm": slope * 1.0e6,
        "correlation_with_vertical_displacement": float(np.corrcoef(gravity, height)[0, 1]),
        "rms_m_s2": float(math.sqrt(np.mean(gravity**2))),
        "peak_to_peak_m_s2": float(np.ptp(gravity)),
    }


def run(config: dict, source: dict) -> dict:
    series = source["series"]
    height = np.asarray(series["vertical_displacement_detided_m"], dtype=float)
    direct = np.asarray(series["direct_attraction_detided_m_s2"], dtype=float)
    elastic = np.asarray(series["combined_elastic_gravity_detided_m_s2"], dtype=float)
    components = {
        "direct_attraction": _component_metrics(direct, height),
        "combined_elastic_gravity": _component_metrics(elastic, height),
        "direct_plus_combined_elastic_gravity_diagnostic": _component_metrics(
            direct + elastic, height
        ),
    }
    target = float(config["published_target_nm_s2_per_mm"])
    elastic_ratio = components["combined_elastic_gravity"]["paper_convention_ratio_nm_s2_per_mm"]
    total_ratio = components["direct_plus_combined_elastic_gravity_diagnostic"][
        "paper_convention_ratio_nm_s2_per_mm"
    ]
    canonical = json.dumps(config, sort_keys=True, separators=(",", ":"))
    return {
        "schema_version": 1,
        "experiment_id": config["experiment_id"],
        "result_class": "registered_component_decomposition_not_observable_redefinition",
        "config_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
        "source_experiment": config["source_experiment"],
        "sample_count": len(height),
        "components": components,
        "published_elastic_comparison": {
            "target_nm_s2_per_mm": target,
            "model_nm_s2_per_mm": elastic_ratio,
            "absolute_difference_nm_s2_per_mm": abs(target - elastic_ratio),
            "fractional_difference": abs(target - elastic_ratio) / abs(target),
        },
        "diagnostic_total_proximity": {
            "direct_plus_elastic_nm_s2_per_mm": total_ratio,
            "absolute_difference_from_published_target_nm_s2_per_mm": abs(target - total_ratio),
            "fractional_difference_from_published_target": abs(target - total_ratio) / abs(target),
            "comparison_authorized": False,
        },
        "component_scale_ratios": {
            "direct_to_elastic_rms": components["direct_attraction"]["rms_m_s2"]
            / components["combined_elastic_gravity"]["rms_m_s2"],
            "direct_to_elastic_peak_to_peak": components["direct_attraction"]["peak_to_peak_m_s2"]
            / components["combined_elastic_gravity"]["peak_to_peak_m_s2"],
        },
        "discrepancy_source_ledger": [
            {
                "source": "Earth/load-response model",
                "project": "LoadDef v1.2.2 PREM/CE",
                "published": "SPOTL Gutenberg-Bullen convention",
                "quantitative_allocation": None,
                "status": "confounded_not_isolated_by_available_registered_runs",
            },
            {
                "source": "tidal removal",
                "project": "30-day eight-constituent harmonic fit with trend",
                "published": "three-year ET34-X-V80 analysis",
                "quantitative_allocation": None,
                "status": "confounded_not_isolated_by_available_registered_series",
            },
            {
                "source": "direct attraction",
                "project": "computed and retained separately",
                "published": "excluded from the registered height-dependent comparison",
                "quantitative_allocation": None,
                "status": "diagnostic_only_not_a_discrepancy_explanation",
            },
        ],
        "claim_boundary": config["claim_boundary"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    root = Path(__file__).resolve().parents[1]
    source = json.loads((root / config["source_metrics"]).read_text())
    result = run(config, source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
