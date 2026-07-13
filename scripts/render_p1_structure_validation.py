"""Render mass-compensation schematics and registered Helgoland components."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np


def render(source: dict, audit: dict, output_svg: Path, output_png: Path) -> None:
    mpl.rcParams["svg.hashsalt"] = "oceangravity-paper1-v1"
    figure, axes = plt.subplots(1, 3, figsize=(13.2, 4.25), layout="constrained")

    axis = axes[0]
    x = np.linspace(-3.0, 3.0, 300)
    gaussian = np.exp(-0.5 * x**2)
    axis.plot(x, gaussian, color="#e67e22", label="positive mass")
    axis.plot(x, -np.exp(-0.5 * (x - 1.8) ** 2), color="#2980b9", label="compensating mass")
    axis.fill_between(x, 0, gaussian, color="#e67e22", alpha=0.25)
    axis.fill_between(x, 0, -np.exp(-0.5 * (x - 1.8) ** 2), color="#2980b9", alpha=0.25)
    axis.annotate(
        "paired compensation / relocation",
        xy=(1.8, 0.72),
        xytext=(-2.6, 0.72),
        arrowprops={"arrowstyle": "->"},
        fontsize=8,
    )
    axis.axhline(0, color="black", linewidth=0.8)
    axis.set_title("a  Conserved/compensated sources", loc="left")
    axis.set_xlabel("Idealized source coordinate")
    axis.set_ylabel("Signed mass anomaly (schematic)")
    axis.legend(fontsize=7, loc="lower left")

    series = source["series"]
    times = np.asarray(
        [datetime.fromisoformat(value.replace("Z", "+00:00")) for value in series["timestamps_utc"]]
    )
    selected = (times >= datetime.fromisoformat("2022-01-29T00:00:00+00:00")) & (
        times <= datetime.fromisoformat("2022-02-01T00:00:00+00:00")
    )
    axis = axes[1]
    direct = np.asarray(series["direct_attraction_detided_m_s2"])[selected] * 1.0e9
    elastic = np.asarray(series["combined_elastic_gravity_detided_m_s2"])[selected] * 1.0e9
    height = np.asarray(series["vertical_displacement_detided_m"])[selected] * 1.0e3
    axis.plot(times[selected], direct, label="direct", color="#d35400")
    axis.plot(times[selected], elastic, label="combined elastic", color="#8e44ad")
    axis.set_ylabel("Gravity component (nm s⁻²)")
    axis.xaxis.set_major_locator(mdates.DayLocator(interval=1, tz=timezone.utc))
    axis.xaxis.set_major_formatter(mdates.DateFormatter("%b %d", tz=timezone.utc))
    axis.tick_params(axis="x", rotation=25)
    second = axis.twinx()
    second.plot(
        times[selected],
        height,
        label="vertical displacement",
        color="#27ae60",
        alpha=0.65,
        linestyle="--",
    )
    second.set_ylabel("Vertical displacement (mm)", color="#27ae60")
    handles, labels = axis.get_legend_handles_labels()
    handles2, labels2 = second.get_legend_handles_labels()
    axis.legend(handles + handles2, labels + labels2, fontsize=7, loc="upper right")
    axis.set_title("b  Helgoland registered event window", loc="left")

    axis = axes[2]
    names = ("Direct", "Combined elastic", "Direct + elastic\n(diagnostic)")
    values = (
        audit["components"]["direct_attraction"]["paper_convention_ratio_nm_s2_per_mm"],
        audit["components"]["combined_elastic_gravity"]["paper_convention_ratio_nm_s2_per_mm"],
        audit["components"]["direct_plus_combined_elastic_gravity_diagnostic"][
            "paper_convention_ratio_nm_s2_per_mm"
        ],
    )
    bars = axis.barh(names, values, color=("#d35400", "#8e44ad", "#95a5a6"))
    bars[-1].set_hatch("//")
    target = audit["published_elastic_comparison"]["target_nm_s2_per_mm"]
    axis.axvline(target, color="black", linestyle="--", label="published -2.684")
    axis.set_xlabel("Paper-convention ratio (nm s⁻² mm⁻¹)")
    axis.set_title("c  Component-to-height regressions", loc="left")
    axis.legend(fontsize=7, loc="lower right")

    figure.suptitle(
        "Physical compensation and component-resolved Helgoland validation", fontsize=12
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
    parser.add_argument("--source-metrics", type=Path, required=True)
    parser.add_argument("--component-audit", type=Path, required=True)
    parser.add_argument("--output-svg", type=Path, required=True)
    parser.add_argument("--output-png", type=Path, required=True)
    args = parser.parse_args()
    render(
        json.loads(args.source_metrics.read_text()),
        json.loads(args.component_audit.read_text()),
        args.output_svg,
        args.output_png,
    )


if __name__ == "__main__":
    main()
