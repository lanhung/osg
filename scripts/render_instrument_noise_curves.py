"""Render deterministic, dependency-free SVG views of instrument ASD anchors."""

from __future__ import annotations

import argparse
import json
import math
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from oceangravity.instruments import NoiseCurve, load_noise_curves  # noqa: E402

WIDTH = 900
HEIGHT = 560
LEFT = 95
RIGHT = 30
TOP = 45
BOTTOM = 85
COLORS = ("#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00")


def _log_ticks(minimum: float, maximum: float) -> list[float]:
    start = math.floor(math.log10(minimum))
    stop = math.ceil(math.log10(maximum))
    return [10.0**power for power in range(start, stop + 1)]


def render_observable(curves: list[NoiseCurve], observable: str) -> str:
    selected = sorted(
        (curve for curve in curves if curve.observable == observable),
        key=lambda curve: curve.instrument_id,
    )
    if not selected:
        raise ValueError(f"no curves for observable {observable!r}")
    units = {curve.asd_unit for curve in selected}
    if len(units) != 1:
        raise ValueError("curves in one panel must have one ASD unit")
    x_min = min(curve.frequencies_hz[0] for curve in selected)
    x_max = max(curve.frequencies_hz[-1] for curve in selected)
    y_min_data = min(min(curve.asd) for curve in selected)
    y_max_data = max(max(curve.asd) for curve in selected)
    y_min = 10.0 ** math.floor(math.log10(y_min_data) - 0.25)
    y_max = 10.0 ** math.ceil(math.log10(y_max_data) + 0.25)
    plot_width = WIDTH - LEFT - RIGHT
    plot_height = HEIGHT - TOP - BOTTOM

    def x_position(value: float) -> float:
        return LEFT + plot_width * math.log(value / x_min) / math.log(x_max / x_min)

    def y_position(value: float) -> float:
        return TOP + plot_height * math.log(y_max / value) / math.log(y_max / y_min)

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#222}.tick{font-size:13px}.label{font-size:15px}.title{font-size:20px;font-weight:600}.legend{font-size:12px}</style>',
        f'<text class="title" x="{WIDTH / 2}" y="27" text-anchor="middle">{escape(observable)} literature/model anchors</text>',
    ]
    for tick in _log_ticks(x_min, x_max):
        if tick < x_min or tick > x_max:
            continue
        x = x_position(tick)
        lines.append(f'<line x1="{x:.3f}" y1="{TOP}" x2="{x:.3f}" y2="{TOP + plot_height}" stroke="#ddd"/>')
        lines.append(f'<text class="tick" x="{x:.3f}" y="{TOP + plot_height + 23}" text-anchor="middle">1e{round(math.log10(tick))}</text>')
    for tick in _log_ticks(y_min, y_max):
        y = y_position(tick)
        lines.append(f'<line x1="{LEFT}" y1="{y:.3f}" x2="{LEFT + plot_width}" y2="{y:.3f}" stroke="#ddd"/>')
        lines.append(f'<text class="tick" x="{LEFT - 12}" y="{y + 4:.3f}" text-anchor="end">1e{round(math.log10(tick))}</text>')
    lines.extend(
        (
            f'<rect x="{LEFT}" y="{TOP}" width="{plot_width}" height="{plot_height}" fill="none" stroke="#222"/>',
            f'<text class="label" x="{LEFT + plot_width / 2}" y="{HEIGHT - 25}" text-anchor="middle">Frequency (Hz)</text>',
            f'<text class="label" transform="translate(23 {TOP + plot_height / 2}) rotate(-90)" text-anchor="middle">ASD ({escape(next(iter(units)))})</text>',
        )
    )
    for index, curve in enumerate(selected):
        color = COLORS[index % len(COLORS)]
        points = " ".join(
            f"{x_position(frequency):.3f},{y_position(asd):.3f}"
            for frequency, asd in zip(curve.frequencies_hz, curve.asd, strict=True)
        )
        lines.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3"/>')
        legend_y = TOP + 17 + 19 * index
        lines.append(f'<line x1="{LEFT + 12}" y1="{legend_y}" x2="{LEFT + 40}" y2="{legend_y}" stroke="{color}" stroke-width="3"/>')
        lines.append(f'<text class="legend" x="{LEFT + 47}" y="{legend_y + 4}">{escape(curve.instrument_id)}</text>')
    lines.append('</svg>')
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    curves = list(load_noise_curves(args.manifest).values())
    args.output_directory.mkdir(parents=True, exist_ok=True)
    outputs = {}
    for observable in ("vertical_gravity", "gravity_gradient"):
        output = args.output_directory / f"instrument_asd_{observable}.svg"
        output.write_text(render_observable(curves, observable), encoding="utf-8")
        outputs[observable] = str(output)
    print(json.dumps(outputs, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
