"""Render the registered Paper 1 frequency-coverage requirement figure."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

PROCESS_ORDER = (
    "mesoscale_eddy",
    "storm_surge",
    "internal_wave",
    "tide",
    "submarine_landslide",
    "tsunami",
)
PROCESS_LABELS = ("Eddy", "Storm surge", "Internal wave", "Tide", "Landslide", "Tsunami")


def render(metrics: dict, instrument_curves: dict, output_svg: Path, output_png: Path) -> None:
    mpl.rcParams["svg.hashsalt"] = "oceangravity-paper1-v1"
    thresholds = tuple(metrics["required_energy_fractions"])
    matrix = np.asarray(
        [
            [
                metrics["process_summary"][process]["thresholds"][str(threshold)]["median_hz"]
                for threshold in thresholds
            ]
            for process in PROCESS_ORDER
        ]
    )
    reviewed_ids = (
        "igrav_quiet_j9_self_noise_anchor",
        "aqg_a01_field_short_term_anchor",
        "fg5_228_short_term_anchor",
    )
    reviewed_curves = {
        row["instrument_id"]: row
        for row in instrument_curves["curves"]
        if row["instrument_id"] in reviewed_ids
    }
    low_edges = {
        curve_id: reviewed_curves[curve_id]["frequencies_hz"][0]
        for curve_id in reviewed_ids
    }
    requirement_90 = matrix[:, thresholds.index(0.9)]
    permissive_gap = min(low_edges.values()) / requirement_90

    figure, axes = plt.subplots(1, 3, figsize=(13.2, 4.4), layout="constrained")
    colors = plt.cm.tab10(np.linspace(0.0, 0.8, len(PROCESS_ORDER)))
    for index, label in enumerate(PROCESS_LABELS):
        axes[0].plot(
            matrix[index],
            np.asarray(thresholds) * 100.0,
            marker="o",
            color=colors[index],
            label=label,
        )
    axes[0].set_xscale("log")
    axes[0].set_xlabel("Maximum admissible lower edge (Hz)")
    axes[0].set_ylabel("Signal-energy coverage (%)")
    axes[0].set_title("a  Inverse cumulative-energy requirement", loc="left")
    axes[0].grid(True, which="both", alpha=0.25)
    axes[0].legend(fontsize=7, ncol=2)

    image = axes[1].imshow(np.log10(matrix), aspect="auto", cmap="viridis")
    axes[1].set_xticks(range(len(thresholds)), [f"{value:.0%}" for value in thresholds])
    axes[1].set_yticks(range(len(PROCESS_LABELS)), PROCESS_LABELS)
    axes[1].set_xlabel("Required energy coverage")
    axes[1].set_title("b  Median lower-edge requirement", loc="left")
    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            axes[1].text(
                column,
                row,
                f"{matrix[row, column]:.1e}",
                ha="center",
                va="center",
                color="white" if np.log10(matrix[row, column]) < -4.2 else "black",
                fontsize=7,
            )
    colorbar = figure.colorbar(image, ax=axes[1], shrink=0.82)
    colorbar.set_label("log10(Hz)")

    axes[2].barh(PROCESS_LABELS, permissive_gap, color=colors, alpha=0.45)
    marker_styles = {
        "igrav_quiet_j9_self_noise_anchor": ("iGrav", "D", "#222222"),
        "aqg_a01_field_short_term_anchor": ("AQG-A01", "o", "#006d77"),
        "fg5_228_short_term_anchor": ("FG5#228", "x", "#9b2226"),
    }
    y_positions = np.arange(len(PROCESS_LABELS))
    for curve_id in reviewed_ids:
        label, marker, color = marker_styles[curve_id]
        axes[2].scatter(
            low_edges[curve_id] / requirement_90,
            y_positions,
            marker=marker,
            color=color,
            s=28,
            label=f"{label}: {low_edges[curve_id]:.0e} Hz",
            zorder=3,
        )
    axes[2].set_xscale("log")
    axes[2].set_xlabel("Published lower edge / 90% requirement")
    axes[2].set_title("c  Low-frequency coverage gap", loc="left")
    axes[2].grid(True, axis="x", which="both", alpha=0.25)
    axes[2].legend(fontsize=7, loc="lower right")
    for row, value in enumerate(permissive_gap):
        axes[2].text(value * 1.08, row, f"{value:.2g}x", va="center", fontsize=8)

    figure.suptitle(
        "Frequency support required before SNR classification (coverage only)", fontsize=12
    )
    output_svg.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_svg, metadata={"Date": None, "Creator": "oceangravity"})
    output_svg.write_text(
        "\n".join(line.rstrip() for line in output_svg.read_text().splitlines()) + "\n"
    )
    figure.savefig(
        output_png,
        dpi=220,
        metadata={"Software": "oceangravity registered renderer"},
    )
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", type=Path, required=True)
    parser.add_argument("--instrument-curves", type=Path, required=True)
    parser.add_argument("--output-svg", type=Path, required=True)
    parser.add_argument("--output-png", type=Path, required=True)
    args = parser.parse_args()
    render(
        json.loads(args.metrics.read_text()),
        json.loads(args.instrument_curves.read_text()),
        args.output_svg,
        args.output_png,
    )


if __name__ == "__main__":
    main()
