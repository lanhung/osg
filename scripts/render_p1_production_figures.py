"""Render the Paper 1 production figure bundle from registered metrics."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PROCESS_ORDER = [
    "tide",
    "storm_surge",
    "mesoscale_eddy",
    "internal_wave",
    "tsunami",
    "submarine_landslide",
]
PROCESS_LABELS = {
    "tide": "M2 tide",
    "storm_surge": "Storm surge",
    "mesoscale_eddy": "Mesoscale eddy",
    "internal_wave": "Internal wave",
    "tsunami": "Tsunami packet",
    "submarine_landslide": "Storegga slide",
}
CURVE_LABELS = {
    "igrav_quiet_j9_self_noise_anchor": "iGrav self-noise",
    "aqg_a01_field_short_term_anchor": "AQG-A01 anchor",
    "fg5_228_short_term_anchor": "FG5#228 anchor",
}
COLORS = {
    "tide": "#0072B2",
    "storm_surge": "#D55E00",
    "mesoscale_eddy": "#009E73",
    "internal_wave": "#CC79A7",
    "tsunami": "#E69F00",
    "submarine_landslide": "#56B4E9",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--metrics",
        type=Path,
        default=ROOT / "experiments/paper1/P1-E006-evidence-bounded-atlas/metrics.json",
    )
    parser.add_argument(
        "--config", type=Path, default=ROOT / "configs/paper1/evidence_bounded_atlas.json"
    )
    parser.add_argument(
        "--curves", type=Path, default=ROOT / "data/manifests/instrument_noise_curves.json"
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--manifest-path",
        type=Path,
        help="Optional manifest path; defaults to OUTPUT_DIR/p1_figure_manifest.json",
    )
    return parser.parse_args()


def _configure_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.labelsize": 9,
            "axes.titlesize": 10,
            "legend.fontsize": 8,
            "svg.hashsalt": "oceangravity-paper1-v1",
        }
    )


def _save(fig: plt.Figure, path: Path) -> None:
    fig.savefig(
        path,
        format="svg",
        bbox_inches="tight",
        metadata={"Date": None, "Creator": "oceangravity registered renderer"},
    )
    path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines()) + "\n")
    fig.savefig(
        path.with_suffix(".png"),
        format="png",
        dpi=180,
        bbox_inches="tight",
        metadata={"Software": "oceangravity registered renderer"},
    )
    plt.close(fig)


def _frequency_ranges(config: dict) -> dict[str, tuple[float, float]]:
    tide_frequency = 1.0 / config["tide"]["period_s"]
    storm_duration = (7.0 * 86400.0, 30.0 * 86400.0)
    eddy_frequency = config["eddy"]["translation_speed_m_s"] / config["eddy"]["horizontal_scale_m"]
    tsunami_speed = math.sqrt(9.80665 * config["tsunami"]["water_depth_m"])
    tsunami_scale = config["tsunami"]["source_width_m"] / 2.0
    slide = config["landslide_storegga"]
    return {
        "tide": (tide_frequency, tide_frequency),
        "storm_surge": (1.0 / storm_duration[1], 1.0 / storm_duration[0]),
        "mesoscale_eddy": (eddy_frequency / 4.0, eddy_frequency),
        "internal_wave": (tide_frequency, tide_frequency),
        "tsunami": (
            tsunami_speed / (config["tsunami"]["source_length_m"][1] + 8.0 * tsunami_scale),
            tsunami_speed / tsunami_scale,
        ),
        "submarine_landslide": (
            slide["velocity_m_s"][0] / slide["runout_m"],
            slide["velocity_m_s"][1] / slide["runout_m"],
        ),
    }


def render_frequency_coverage(config: dict, curves: dict, path: Path) -> None:
    ranges = _frequency_ranges(config)
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    for index, process in enumerate(PROCESS_ORDER):
        lower, upper = ranges[process]
        if lower == upper:
            ax.scatter(lower, index, color=COLORS[process], s=34, zorder=3)
        else:
            ax.hlines(index, lower, upper, color=COLORS[process], linewidth=5)
            ax.scatter([lower, upper], [index, index], color=COLORS[process], s=18)
    base = len(PROCESS_ORDER) + 0.4
    admitted = set(config["authorized_vertical_gravity_curves"])
    admitted_rows = [row for row in curves["curves"] if row["instrument_id"] in admitted]
    for offset, curve in enumerate(admitted_rows):
        y = base + offset
        ax.hlines(
            y,
            curve["frequencies_hz"][0],
            curve["frequencies_hz"][-1],
            color="#333333",
            linewidth=7,
        )
    labels = [PROCESS_LABELS[item] for item in PROCESS_ORDER] + [
        CURVE_LABELS[row["instrument_id"]]
        for row in curves["curves"]
        if row["instrument_id"] in admitted
    ]
    positions = list(range(len(PROCESS_ORDER))) + [
        base + index for index in range(len(labels) - len(PROCESS_ORDER))
    ]
    ax.set_yticks(positions, labels)
    ax.axvline(1e-3, color="#777777", linestyle="--", linewidth=0.8)
    ax.text(
        1.08e-3,
        len(PROCESS_ORDER) - 0.25,
        "lowest admitted curve edge",
        color="#555555",
        fontsize=8,
    )
    ax.set_xscale("log")
    ax.set_xlabel("Characteristic frequency or range (Hz)")
    ax.set_title("Process timescales versus admitted vertical-gravity curve support")
    ax.grid(axis="x", which="both", alpha=0.2)
    ax.invert_yaxis()
    _save(fig, path)


def _distance_envelopes(metrics: dict):
    grouped: dict[tuple[str, float], list[float]] = defaultdict(list)
    for record in metrics["records"]:
        distance = record["distance_standoff_m"]
        if distance is not None:
            grouped[(record["process"], distance)].append(
                record["peak_absolute_direct_gravity_m_s2"]
            )
    return grouped


def render_distance_envelopes(metrics: dict, path: Path) -> None:
    grouped = _distance_envelopes(metrics)
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    for process in PROCESS_ORDER:
        distances = sorted(distance for item, distance in grouped if item == process)
        if not distances:
            continue
        values = [sorted(grouped[(process, distance)]) for distance in distances]
        low = np.array([row[0] for row in values])
        median = np.array([row[len(row) // 2] for row in values])
        high = np.array([row[-1] for row in values])
        x = np.asarray(distances) / 1000.0
        ax.plot(x, median, marker="o", color=COLORS[process], label=PROCESS_LABELS[process])
        if np.any(high > low):
            ax.fill_between(x, low, high, color=COLORS[process], alpha=0.16)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Surface standoff from represented source support (km)")
    ax.set_ylabel("Peak absolute direct radial gravity (m s$^{-2}$)")
    ax.set_title("Evidence-bounded direct-gravity amplitude envelopes")
    ax.grid(which="both", alpha=0.2)
    ax.legend(ncol=2, frameon=False)
    _save(fig, path)


def render_coverage_matrix(metrics: dict, config: dict, path: Path) -> None:
    curves = config["authorized_vertical_gravity_curves"]
    matrix = np.zeros((len(PROCESS_ORDER), len(curves)))
    annotations = []
    for row_index, process in enumerate(PROCESS_ORDER):
        row_annotations = []
        for column_index, curve in enumerate(curves):
            counts = metrics["status_summary"][process][curve]
            total = sum(counts.values())
            partial = counts.get("partial_band_not_classified", 0)
            no_coverage = counts.get("no_frequency_coverage", 0)
            matrix[row_index, column_index] = partial / total if total else 0.0
            row_annotations.append(
                f"partial {partial}/{total}" if partial else f"no band {no_coverage}/{total}"
            )
        annotations.append(row_annotations)
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    image = ax.imshow(matrix, vmin=0.0, vmax=1.0, cmap="Blues", aspect="auto")
    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            ax.text(column, row, annotations[row][column], ha="center", va="center", fontsize=7)
    ax.set_xticks(
        range(len(curves)),
        [CURVE_LABELS[item] for item in curves],
        rotation=20,
        ha="right",
    )
    ax.set_yticks(range(len(PROCESS_ORDER)), [PROCESS_LABELS[item] for item in PROCESS_ORDER])
    ax.set_title("Signal-energy coverage gate (no SNR classification below 90%)")
    colorbar = fig.colorbar(image, ax=ax, fraction=0.035, pad=0.03)
    colorbar.set_label("Fraction of records with partial band")
    _save(fig, path)


def render_sensitivity_panel(metrics: dict, path: Path) -> None:
    grouped = _distance_envelopes(metrics)
    selected = ["internal_wave", "tsunami", "submarine_landslide"]
    fig, axes = plt.subplots(1, 3, figsize=(8.2, 3.3), sharex=True, sharey=True)
    for ax, process in zip(axes, selected, strict=True):
        distances = sorted(distance for item, distance in grouped if item == process)
        x = np.asarray(distances) / 1000.0
        values = [np.asarray(grouped[(process, distance)]) for distance in distances]
        low = np.array([row.min() for row in values])
        median = np.array([np.median(row) for row in values])
        high = np.array([row.max() for row in values])
        ax.fill_between(x, low, high, color=COLORS[process], alpha=0.22)
        ax.plot(x, median, color=COLORS[process], marker="o", linewidth=1.5)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_title(PROCESS_LABELS[process])
        ax.grid(which="both", alpha=0.2)
    axes[0].set_ylabel("Peak direct radial gravity (m s$^{-2}$)")
    axes[1].set_xlabel("Surface standoff (km)")
    fig.suptitle("Sensitivity envelopes; shading is not a probability interval", y=1.02)
    _save(fig, path)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _manifest_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def run(metrics: dict, config: dict, curves: dict, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    _configure_style()
    assets = {
        "frequency_coverage": output_dir / "p1_frequency_coverage.svg",
        "distance_amplitude_envelopes": output_dir / "p1_distance_amplitude_envelopes.svg",
        "process_instrument_coverage_matrix": output_dir / "p1_process_instrument_matrix.svg",
        "sensitivity_envelopes": output_dir / "p1_sensitivity_envelopes.svg",
    }
    render_frequency_coverage(config, curves, assets["frequency_coverage"])
    render_distance_envelopes(metrics, assets["distance_amplitude_envelopes"])
    render_coverage_matrix(metrics, config, assets["process_instrument_coverage_matrix"])
    render_sensitivity_panel(metrics, assets["sensitivity_envelopes"])
    return {
        "schema_version": 1,
        "source_experiment": metrics["experiment_id"],
        "assets": {
            asset_id: {
                "path": _manifest_path(path),
                "sha256": sha256_file(path),
                "preview_png_path": _manifest_path(path.with_suffix(".png")),
                "preview_png_sha256": sha256_file(path.with_suffix(".png")),
                "status": "complete",
            }
            for asset_id, path in assets.items()
        },
    }


def main() -> int:
    args = parse_args()
    metrics = json.loads(args.metrics.read_text(encoding="utf-8"))
    config = json.loads(args.config.read_text(encoding="utf-8"))
    curves = json.loads(args.curves.read_text(encoding="utf-8"))
    manifest = run(metrics, config, curves, args.output_dir)
    manifest_path = args.manifest_path or args.output_dir / "p1_figure_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
