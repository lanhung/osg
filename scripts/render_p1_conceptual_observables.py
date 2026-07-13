"""Render the Paper 1 observable-separation concept figure."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


def _box(axis, xy, width, height, text, color, *, fontsize=9, linestyle="-"):
    patch = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.02",
        facecolor=color,
        edgecolor="#263238",
        linewidth=1.2,
        linestyle=linestyle,
    )
    axis.add_patch(patch)
    axis.text(
        xy[0] + width / 2,
        xy[1] + height / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
    )


def _arrow(axis, start, end, *, color="#455a64", linestyle="-"):
    axis.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=12,
            linewidth=1.4,
            color=color,
            linestyle=linestyle,
        )
    )


def render(output_svg: Path, output_png: Path) -> None:
    mpl.rcParams["svg.hashsalt"] = "oceangravity-paper1-v1"
    figure, axis = plt.subplots(figsize=(12.5, 5.2), layout="constrained")
    axis.set_xlim(0, 13.4)
    axis.set_ylim(0, 6.0)
    axis.axis("off")

    _box(
        axis,
        (0.2, 2.25),
        2.2,
        1.5,
        "Ocean processes\nTide | surge | eddy\nInternal wave | tsunami | slide",
        "#d7ecff",
    )
    _box(
        axis,
        (3.0, 2.45),
        1.9,
        1.1,
        "Mass anomaly\n" + r"$\Delta\sigma(x,t)$ or $\rho'(x,z,t)$",
        "#e8f5e9",
    )
    _arrow(axis, (2.4, 3.0), (3.0, 3.0))

    _box(axis, (5.6, 4.25), 2.25, 1.0, "Newtonian kernel\ndirect attraction", "#fff3cd")
    _box(axis, (8.6, 4.25), 2.35, 1.0, "Direct radial gravity\ngdirect  [m s⁻²]", "#ffe0b2")
    _arrow(axis, (4.9, 3.25), (5.6, 4.65))
    _arrow(axis, (7.85, 4.75), (8.6, 4.75))

    _box(
        axis,
        (5.6, 2.45),
        2.25,
        1.0,
        "Elastic Earth response\nLove numbers / Green functions",
        "#e1bee7",
    )
    _box(
        axis,
        (8.6, 2.45),
        2.35,
        1.0,
        "Combined elastic gravity\nand vertical displacement uz",
        "#f3e5f5",
        fontsize=8.5,
    )
    _arrow(axis, (4.9, 3.0), (5.6, 3.0), color="#6a1b9a")
    _arrow(axis, (7.85, 3.0), (8.6, 3.0), color="#6a1b9a")
    axis.text(6.7, 2.18, "surface-load branches only", ha="center", fontsize=8, color="#6a1b9a")

    _box(axis, (5.6, 0.65), 2.25, 0.9, "Spatial derivative\nTzz  [s⁻²]", "#d1c4e9", linestyle="--")
    _box(
        axis,
        (8.6, 0.65),
        2.35,
        0.9,
        "Gravity-gradient instruments\nSupplement / future work",
        "#ede7f6",
        fontsize=8.5,
        linestyle="--",
    )
    _arrow(axis, (4.9, 2.75), (5.6, 1.15), color="#5e35b1", linestyle="--")
    _arrow(axis, (7.85, 1.1), (8.6, 1.1), color="#5e35b1", linestyle="--")

    _box(
        axis,
        (11.35, 3.75),
        1.75,
        1.95,
        "Coverage gate\n\nSame observable\n+ units\n+ frequency band\n+ energy fraction",
        "#ffcdd2",
        fontsize=7.8,
    )
    _arrow(axis, (10.95, 4.75), (11.35, 4.75), color="#c62828")
    axis.text(
        12.22,
        3.55,
        "No coverage → no SNR classification",
        ha="center",
        va="top",
        fontsize=8,
        color="#b71c1c",
    )

    axis.text(
        0.2,
        5.75,
        "Paper 1 observable framework: components remain separate until comparison is authorized",
        fontsize=13,
        weight="bold",
    )
    axis.text(
        0.2,
        0.1,
        "P1-E006/P1-E008: direct radial gravity for all six families   |   "
        "Helgoland: components separate   |   Total observable: not inferred",
        fontsize=8.2,
        color="#37474f",
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
    parser.add_argument("--output-svg", type=Path, required=True)
    parser.add_argument("--output-png", type=Path, required=True)
    args = parser.parse_args()
    render(args.output_svg, args.output_png)


if __name__ == "__main__":
    main()
