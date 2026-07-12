"""Render deterministic engineering distance-attenuation SVG panels."""

from __future__ import annotations

import argparse
import json
import math
from html import escape
from pathlib import Path

WIDTH = 920
HEIGHT = 580
LEFT = 100
RIGHT = 35
TOP = 50
BOTTOM = 85
COLORS = ("#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9")


def render_metric(document: dict, metric: str, y_label: str) -> str:
    processes = document["processes"]
    if not processes:
        raise ValueError("distance experiment has no process records")
    all_records = [record for records in processes.values() for record in records]
    distances = [record["vertical_standoff_m"] for record in all_records]
    values = [record[metric] for record in all_records]
    if not all(value > 0.0 and math.isfinite(value) for value in distances + values):
        raise ValueError("logarithmic distance figures require finite positive values")
    x_min, x_max = min(distances), max(distances)
    y_min = 10.0 ** math.floor(math.log10(min(values)))
    y_max = 10.0 ** math.ceil(math.log10(max(values)))
    plot_width = WIDTH - LEFT - RIGHT
    plot_height = HEIGHT - TOP - BOTTOM

    def x_pos(value: float) -> float:
        return LEFT + plot_width * math.log(value / x_min) / math.log(x_max / x_min)

    def y_pos(value: float) -> float:
        return TOP + plot_height * math.log(y_max / value) / math.log(y_max / y_min)

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#222}.tick{font-size:13px}.label{font-size:15px}.title{font-size:19px;font-weight:600}.legend{font-size:12px}</style>',
        f'<text class="title" x="{WIDTH / 2}" y="29" text-anchor="middle">Engineering distance attenuation: {escape(y_label)}</text>',
    ]
    for exponent in range(math.floor(math.log10(x_min)), math.ceil(math.log10(x_max)) + 1):
        tick = 10.0**exponent
        if x_min <= tick <= x_max:
            x = x_pos(tick)
            lines.append(f'<line x1="{x:.3f}" y1="{TOP}" x2="{x:.3f}" y2="{TOP + plot_height}" stroke="#ddd"/>')
            lines.append(f'<text class="tick" x="{x:.3f}" y="{TOP + plot_height + 23}" text-anchor="middle">1e{exponent}</text>')
    for exponent in range(math.floor(math.log10(y_min)), math.ceil(math.log10(y_max)) + 1):
        tick = 10.0**exponent
        y = y_pos(tick)
        lines.append(f'<line x1="{LEFT}" y1="{y:.3f}" x2="{LEFT + plot_width}" y2="{y:.3f}" stroke="#ddd"/>')
        lines.append(f'<text class="tick" x="{LEFT - 12}" y="{y + 4:.3f}" text-anchor="end">1e{exponent}</text>')
    lines.extend(
        (
            f'<rect x="{LEFT}" y="{TOP}" width="{plot_width}" height="{plot_height}" fill="none" stroke="#222"/>',
            f'<text class="label" x="{LEFT + plot_width / 2}" y="{HEIGHT - 23}" text-anchor="middle">Vertical standoff (m)</text>',
            f'<text class="label" transform="translate(23 {TOP + plot_height / 2}) rotate(-90)" text-anchor="middle">{escape(y_label)}</text>',
        )
    )
    for index, (name, records) in enumerate(sorted(processes.items())):
        color = COLORS[index % len(COLORS)]
        points = " ".join(
            f"{x_pos(record['vertical_standoff_m']):.3f},{y_pos(record[metric]):.3f}"
            for record in records
        )
        lines.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2.5"/>')
        for record in records:
            lines.append(f'<circle cx="{x_pos(record["vertical_standoff_m"]):.3f}" cy="{y_pos(record[metric]):.3f}" r="2.6" fill="{color}"/>')
        legend_y = TOP + 17 + 18 * index
        lines.append(f'<line x1="{LEFT + 12}" y1="{legend_y}" x2="{LEFT + 38}" y2="{legend_y}" stroke="{color}" stroke-width="3"/>')
        lines.append(f'<text class="legend" x="{LEFT + 45}" y="{legend_y + 4}">{escape(name)}</text>')
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    document = json.loads(args.metrics.read_text(encoding="utf-8"))
    args.output_directory.mkdir(parents=True, exist_ok=True)
    outputs = {
        "gravity": (
            "distance_attenuation_gravity.svg",
            "peak_absolute_direct_gravity_m_s2",
            "Peak direct vertical gravity (m s^-2)",
        ),
        "gradient": (
            "distance_attenuation_Tzz.svg",
            "peak_absolute_direct_Tzz_s2",
            "Peak absolute Tzz (s^-2)",
        ),
    }
    for filename, metric, label in outputs.values():
        (args.output_directory / filename).write_text(
            render_metric(document, metric, label), encoding="utf-8"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
