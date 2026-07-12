"""Audit gaps, response removal and diagnostic low-frequency noise metrics."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from obspy import read, read_inventory
from scipy.signal import welch

ROOT = Path(__file__).resolve().parents[1]


def diagnostic_band_metrics(
    values: np.ndarray, sample_rate_hz: float, band_hz: tuple[float, float]
) -> dict:
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or values.size < 16 or not np.all(np.isfinite(values)):
        raise ValueError("diagnostic values must be a finite one-dimensional series")
    frequencies, psd = welch(
        values,
        fs=float(sample_rate_hz),
        window="hann",
        nperseg=min(1024, values.size),
        detrend="constant",
        scaling="density",
    )
    selected = (frequencies >= band_hz[0]) & (frequencies <= band_hz[1])
    if np.count_nonzero(selected) < 2:
        raise ValueError("diagnostic band contains fewer than two Welch bins")
    band_frequency = frequencies[selected]
    band_psd = psd[selected]
    return {
        "welch_bin_count": int(band_frequency.size),
        "median_asd_m_s2_per_sqrt_hz": float(np.median(np.sqrt(band_psd))),
        "band_rms_m_s2": float(np.sqrt(np.trapezoid(band_psd, band_frequency))),
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(config: dict, retrieval: dict) -> dict:
    processing = config["processing"]
    band = tuple(map(float, processing["diagnostic_band_hz"]))
    records = []
    vertical_by_window: dict[str, dict[str, tuple[np.ndarray, float, float]]] = {}
    for row in retrieval["requests"]:
        if row["status"] != "retrieved":
            records.append(
                {
                    "window_id": row["window_id"],
                    "split_role": row["split_role"],
                    "environment_label": row["label_status"],
                    "station_id": f"{row['network']}.{row['station']}",
                    "location": row["location"],
                    "retrieval_status": row["status"],
                    "response_removed": False,
                    "component_metrics": [],
                }
            )
            continue
        raw_path = ROOT / row["raw_path"]
        if _sha256(raw_path) != row["sha256"]:
            raise ValueError(f"raw checksum mismatch: {row['raw_path']}")
        stream = read(raw_path)
        expected_channels = set(row["channels"])
        location = "" if row["location"] == "--" else row["location"]
        stream = stream.select(network=row["network"], station=row["station"], location=location)
        present_channels = {trace.stats.channel for trace in stream}
        gaps = stream.get_gaps()
        response_path = ROOT / (f"data/raw/paper3/responses/{row['network']}.{row['station']}.xml")
        response_removed = False
        component_metrics = []
        if present_channels == expected_channels and not gaps and len(stream) == 3:
            inventory = read_inventory(response_path)
            processed = stream.copy()
            processed.detrend("linear")
            processed.taper(max_percentage=0.05, type="cosine")
            try:
                processed.remove_response(
                    inventory=inventory,
                    output=processing["response_output"],
                    pre_filt=tuple(processing["pre_filt_hz"]),
                    water_level=float(processing["water_level_db"]),
                )
            except Exception as error:  # ObsPy response subclasses vary by network.
                response_error = f"{type(error).__name__}: {error}"
            else:
                response_error = None
                response_removed = True
                for trace in sorted(processed, key=lambda item: item.stats.channel):
                    metrics = diagnostic_band_metrics(
                        trace.data, float(trace.stats.sampling_rate), band
                    )
                    metrics.update(
                        {
                            "channel": trace.stats.channel,
                            "sample_count": int(trace.stats.npts),
                            "sample_rate_hz": float(trace.stats.sampling_rate),
                            "rms_acceleration_m_s2": float(
                                math.sqrt(np.mean(np.asarray(trace.data, dtype=float) ** 2))
                            ),
                        }
                    )
                    component_metrics.append(metrics)
                    if trace.stats.channel.endswith("Z"):
                        vertical_by_window.setdefault(row["window_id"], {})[
                            f"{row['network']}.{row['station']}"
                        ] = (
                            np.asarray(trace.data, dtype=float),
                            float(trace.stats.starttime.timestamp),
                            float(trace.stats.sampling_rate),
                        )
        else:
            response_error = "channel_set_gap_or_trace_count_gate_failed"
        records.append(
            {
                "window_id": row["window_id"],
                "split_role": row["split_role"],
                "environment_label": row["label_status"],
                "station_id": f"{row['network']}.{row['station']}",
                "location": row["location"],
                "expected_channels": sorted(expected_channels),
                "present_channels": sorted(present_channels),
                "gap_or_overlap_count": len(gaps),
                "response_removed": response_removed,
                "response_error": response_error,
                "component_metrics": component_metrics,
            }
        )
    window_correlations = []
    expected_station_count = len(config["stations"])
    for window in config["windows"]:
        rows = vertical_by_window.get(window["window_id"], {})
        if len(rows) != expected_station_count:
            window_correlations.append(
                {"window_id": window["window_id"], "status": "incomplete_station_network"}
            )
            continue
        station_ids = sorted(rows)
        starts = {rows[station][1] for station in station_ids}
        rates = {rows[station][2] for station in station_ids}
        counts = {len(rows[station][0]) for station in station_ids}
        if len(starts) != 1 or len(rates) != 1 or len(counts) != 1:
            window_correlations.append(
                {"window_id": window["window_id"], "status": "time_alignment_failed"}
            )
            continue
        count = counts.pop()
        matrix = np.vstack([rows[station][0] for station in station_ids])
        window_correlations.append(
            {
                "window_id": window["window_id"],
                "status": "descriptive_unclassified_only",
                "station_ids": station_ids,
                "complete_sample_count": count,
                "correlation": np.corrcoef(matrix).tolist(),
            }
        )
    successful = sum(row["response_removed"] for row in records)
    return {
        "schema_version": 1,
        "request_id": config["manifest_id"],
        "result_class": "unclassified_open_archive_noise_qc_not_pegs_detectability",
        "record_count": len(records),
        "response_removed_record_count": successful,
        "all_records_pass_response_qc": successful == len(records),
        "records": records,
        "window_cross_station_correlations": window_correlations,
        "threshold_calibration_authorized": False,
        "pegs_detectability_ready": False,
        "remaining_gate": "earthquake_weather_transient_and_split-label_review",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--retrieval", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run(
        json.loads(args.config.read_text(encoding="utf-8")),
        json.loads(args.retrieval.read_text(encoding="utf-8")),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
