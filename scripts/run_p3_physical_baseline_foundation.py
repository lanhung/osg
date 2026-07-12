"""Run the registered dependency-free Paper 3 physical-baseline fixture."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from oceangravity.evaluation import QuietScoreWindow  # noqa: E402
from oceangravity.pegs import (  # noqa: E402
    SourceTemplateHypothesis,
    audit_single_station_energy_baseline,
    independent_noise_network_template_scores,
    invert_discrete_source_library,
)


def run(config: dict) -> dict:
    if config.get("schema_version") != 1:
        raise ValueError("unsupported Paper 3 foundation schema version")
    station_series = config["station_series"]
    template_scores = independent_noise_network_template_scores(
        station_series,
        config["station_templates"],
        config["station_noise_standard_deviation"],
        config["station_noise_scale_source_ids"],
        sample_interval_s=config["sample_interval_s"],
        decision_step_samples=config["decision_step_samples"],
    )
    quiets = tuple(QuietScoreWindow(**row) for row in config["quiet_score_windows"])
    energy_audit = audit_single_station_energy_baseline(
        quiets,
        config["heldout_event_scores"],
        target_false_alarms_per_30_days=config["target_false_alarms_per_30_days"],
    )
    event_observations = {
        station_id: tuple(values[-2:]) for station_id, values in station_series.items()
    }
    inversion = invert_discrete_source_library(
        event_observations,
        tuple(SourceTemplateHypothesis(**row) for row in config["source_hypotheses"]),
        config["station_noise_standard_deviation"],
        config["station_noise_scale_source_ids"],
        source_library_id=config["source_library_id"],
        sample_interval_s=config["sample_interval_s"],
        window_start_time_since_origin_s=0.0,
    )
    canonical = json.dumps(config, sort_keys=True, separators=(",", ":"))
    return {
        "schema_version": 1,
        "experiment_id": "P3-E001-physical-baseline-foundation",
        "result_class": config["result_class"],
        "config_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
        "scientific_claim_ready": False,
        "claim_blockers": [
            "engineering_fixture_not_validated_pegs_waveforms",
            "synthetic_independent_noise_only",
            "heldout_quiet_exposure_cannot_resolve_target_false_alarm_rate",
        ],
        "network_template_scores": asdict(template_scores),
        "single_station_energy_audit": asdict(energy_audit),
        "discrete_source_inversion": asdict(inversion),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run(json.loads(args.config.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
