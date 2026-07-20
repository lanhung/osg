"""Export self-contained Paper 1 supplementary tables from frozen artifacts."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _tex(value: object) -> str:
    text = str(value)
    for source, replacement in (
        ("\\", r"\textbackslash{}"),
        ("_", r"\_"),
        ("%", r"\%"),
        ("&", r"\&"),
        ("#", r"\#"),
    ):
        text = text.replace(source, replacement)
    return text


def _number(value: float) -> str:
    number = float(value)
    if number == 0.0:
        return "0"
    exponent = math.floor(math.log10(abs(number)))
    if exponent >= 4 or exponent <= -3:
        coefficient = number / 10**exponent
        return rf"${coefficient:.4g}\times10^{{{exponent}}}$"
    return f"{number:.6g}"


def _parameter_rows(config: dict) -> list[tuple[str, str, object, str, str]]:
    return [
        ("Tide", "M2 period", config["tide"]["period_s"], "s", "fixed"),
        (
            "Tide",
            "observation duration",
            "--".join(map(str, config["tide"]["observation_duration_s"])),
            "s",
            "log-midpoint design",
        ),
        ("Tide", "disk radius", config["tide"]["disk_radius_m"], "m", "fixed"),
        (
            "Tide",
            "SSH normalization",
            config["tide"]["sea_level_normalization_m"],
            "m",
            "geometry diagnostic",
        ),
        (
            "Eddy",
            "peak SSH anomaly",
            config["eddy"]["peak_sea_level_anomaly_m"],
            "m",
            "catalogue mean",
        ),
        ("Eddy", "horizontal scale", config["eddy"]["horizontal_scale_m"], "m", "fixed"),
        (
            "Eddy",
            "translation speed",
            config["eddy"]["translation_speed_m_s"],
            "m s$^{-1}$",
            "derived catalogue mean",
        ),
        (
            "Internal wave",
            "peak density anomaly",
            "--".join(map(str, config["internal_wave"]["peak_density_anomaly_kg_m3"])),
            "kg m$^{-3}$",
            "linear-midpoint sensitivity",
        ),
        (
            "Internal wave",
            "horizontal scale",
            "--".join(map(str, config["internal_wave"]["horizontal_scale_m"])),
            "m",
            "linear-midpoint sensitivity",
        ),
        (
            "Internal wave",
            "period",
            config["internal_wave"]["period_s"],
            "s",
            "M2 branch",
        ),
        (
            "Internal wave",
            "vertical scale / lobe separation",
            (
                f"{config['internal_wave']['vertical_scale_m']} / "
                f"{config['internal_wave']['lobe_separation_m']}"
            ),
            "m",
            "exact mass compensation",
        ),
        (
            "Tsunami",
            "deep-ocean crest amplitude",
            "--".join(map(str, config["tsunami"]["deep_ocean_amplitude_m"])),
            "m",
            "linear-midpoint sensitivity",
        ),
        (
            "Tsunami",
            "crest--trough separation",
            "--".join(map(str, config["tsunami"]["source_length_m"])),
            "m",
            "linear-midpoint sensitivity",
        ),
        ("Tsunami", "source width", config["tsunami"]["source_width_m"], "m", "fixed"),
        ("Tsunami", "water depth", config["tsunami"]["water_depth_m"], "m", "fixed"),
        (
            "Landslide",
            "slide volume",
            "--".join(map(str, config["landslide_storegga"]["slide_volume_m3"])),
            "m$^3$",
            "linear-midpoint sensitivity",
        ),
        (
            "Landslide",
            "density contrast",
            config["landslide_storegga"]["bulk_density_contrast_kg_m3"],
            "kg m$^{-3}$",
            "fixed",
        ),
        (
            "Landslide",
            "runout",
            config["landslide_storegga"]["runout_m"],
            "m",
            "fixed",
        ),
        (
            "Landslide",
            "velocity",
            "--".join(map(str, config["landslide_storegga"]["velocity_m_s"])),
            "m s$^{-1}$",
            "linear-midpoint sensitivity",
        ),
        (
            "All idealized families",
            "surface standoff",
            ", ".join(str(value) for value in config["distance_standoff_m"]),
            "m",
            "fixed design; storm excluded",
        ),
    ]


def process_parameter_table(config: dict) -> str:
    lines = [
        r"\begin{tabular}{lllll}",
        r"\toprule",
        r"Process & Parameter & Value/range & Unit & Design interpretation \\",
        r"\midrule",
    ]
    for process, parameter, value, unit, interpretation in _parameter_rows(config):
        display = _number(value) if isinstance(value, (float, int)) else _tex(value)
        lines.append(
            f"{_tex(process)} & {_tex(parameter)} & {display} & {unit} & "
            f"{_tex(interpretation)} \\\\"
        )
    lines.extend((r"\bottomrule", r"\end{tabular}"))
    return "\n".join(lines) + "\n"


def record_registry_table(metrics: dict) -> str:
    grouped: dict[str, list[dict]] = {}
    for row in metrics["records"]:
        grouped.setdefault(row["process"], []).append(row)
    lines = [
        r"\begin{tabular}{lrrrrrr}",
        r"\toprule",
        (
            r"Process & Records & $N$ range & $\Delta t$ range (s) & "
            r"Duration range (s) & $\Delta f$ range (Hz) & Nyquist range (Hz) \\"
        ),
        r"\midrule",
    ]
    for process, rows in sorted(grouped.items()):
        counts = np.asarray([row["sample_count"] for row in rows])
        intervals = np.asarray([row["sample_interval_s"] for row in rows])
        durations = counts * intervals
        spacing = 1.0 / durations
        nyquist = 0.5 / intervals
        values = (
            _tex(process),
            str(len(rows)),
            f"{counts.min()}--{counts.max()}",
            f"{_number(intervals.min())}--{_number(intervals.max())}",
            f"{_number(durations.min())}--{_number(durations.max())}",
            f"{_number(spacing.min())}--{_number(spacing.max())}",
            f"{_number(nyquist.min())}--{_number(nyquist.max())}",
        )
        lines.append(" & ".join(values) + r" \\")
    lines.extend((r"\bottomrule", r"\end{tabular}"))
    return "\n".join(lines) + "\n"


def frequency_requirement_table(metrics: dict) -> str:
    lines = [
        r"\begin{tabular}{lrrrrrr}",
        r"\toprule",
        (
            r"Process & $f_{50}$ median & $f_{75}$ median & $f_{90}$ min & "
            r"$f_{90}$ median & $f_{90}$ max & $f_{95}$ median \\"
        ),
        r"\midrule",
    ]
    for process, row in sorted(metrics["process_summary"].items()):
        threshold = row["thresholds"]
        values = (
            _tex(process),
            _number(threshold["0.5"]["median_hz"]),
            _number(threshold["0.75"]["median_hz"]),
            _number(threshold["0.9"]["minimum_hz"]),
            _number(threshold["0.9"]["median_hz"]),
            _number(threshold["0.9"]["maximum_hz"]),
            _number(threshold["0.95"]["median_hz"]),
        )
        lines.append(" & ".join(values) + r" \\")
    lines.extend((r"\bottomrule", r"\end{tabular}"))
    return "\n".join(lines) + "\n"


def instrument_evidence_table(manifest: dict) -> str:
    lines = [
        r"\begin{tabular}{llllll}",
        r"\toprule",
        (
            r"Instrument/reference & Observable & Band (Hz) & ASD (SI/\sqrt{Hz}) & "
            r"Evidence type & DOI \\"
        ),
        r"\midrule",
    ]
    for curve in manifest["curves"]:
        values = (
            _tex(curve["instrument_id"]),
            _tex(curve["observable"]),
            f"{_number(curve['frequencies_hz'][0])}--{_number(curve['frequencies_hz'][-1])}",
            _number(curve["asd"][0]),
            _tex(curve["interpretation"]),
            rf"\url{{{curve['source']}}}",
        )
        lines.append(" & ".join(values) + r" \\")
    lines.extend((r"\bottomrule", r"\end{tabular}"))
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config", type=Path, default=ROOT / "configs/paper1/evidence_bounded_atlas.json"
    )
    parser.add_argument(
        "--frequency-metrics",
        type=Path,
        default=ROOT / "experiments/paper1/P1-E008-frequency-coverage-requirements/metrics.json",
    )
    parser.add_argument(
        "--instrument-manifest",
        type=Path,
        default=ROOT / "data/manifests/instrument_noise_curves_reviewed_v2.json",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "papers/paper1_journal_of_geodesy/generated"
    )
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    frequency_metrics = json.loads(args.frequency_metrics.read_text())
    instrument_manifest = json.loads(args.instrument_manifest.read_text())
    args.output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "process_parameters.tex": process_parameter_table(config),
        "record_registry.tex": record_registry_table(frequency_metrics),
        "frequency_requirements.tex": frequency_requirement_table(frequency_metrics),
        "instrument_evidence.tex": instrument_evidence_table(instrument_manifest),
    }
    for filename, content in outputs.items():
        (args.output_dir / filename).write_text(content, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
