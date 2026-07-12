"""Generate deterministic six-process direct-gravity foundation metrics."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from oceangravity.constants import MICROGAL, STANDARD_GRAVITY  # noqa: E402
from oceangravity.processes import (  # noqa: E402
    asymmetric_gaussian_disk_surge,
    mass_conserving_submarine_landslide,
    oscillating_compensated_gaussian_dipole,
    periodic_disk_tide,
    propagating_compensated_gaussian_tsunami,
    regular_times,
    translating_gaussian_surface_eddy,
)
from oceangravity.signal_processing import one_sided_spectrum  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def _dominant_nonzero_frequency(values: tuple[float, ...], interval: float) -> float:
    spectrum = one_sided_spectrum(values, interval, detrend="constant")
    index = max(
        range(1, len(spectrum.fourier_amplitude)),
        key=lambda item: abs(spectrum.fourier_amplitude[item]),
    )
    return spectrum.frequencies_hz[index]


def _signal_metrics(signal, interval: float) -> dict[str, float | str]:
    return {
        "model_scope": signal.model_scope,
        "peak_absolute_direct_gravity_m_s2": signal.peak_absolute_gravity_m_s2,
        "peak_absolute_direct_gravity_microgal": signal.peak_absolute_gravity_m_s2 / MICROGAL,
        "dominant_nonzero_frequency_hz": _dominant_nonzero_frequency(
            signal.vertical_direct_gravity_m_s2, interval
        ),
    }


def build_process_signals(config: dict) -> dict[str, tuple[object, float, dict[str, float]]]:
    """Construct the six frozen process signals for reuse by registered experiments."""

    tide_config = config["tide"]
    tide_interval = tide_config["period_s"] / 64.0
    tide_times = regular_times(128, tide_interval)
    tide = periodic_disk_tide(tide_times, **tide_config)

    surge_config = config["storm_surge"]
    surge_interval = 300.0
    surge_times = regular_times(505, surge_interval, start_time_s=-12.0 * 3600.0)
    surge = asymmetric_gaussian_disk_surge(surge_times, **surge_config)

    eddy_config = config["eddy"]
    eddy_characteristic_time = eddy_config["horizontal_scale_m"] / abs(
        eddy_config["translation_speed_x_m_s"]
    )
    eddy_interval = eddy_characteristic_time / 5.0
    eddy_times = regular_times(41, eddy_interval, start_time_s=-4.0 * eddy_characteristic_time)
    eddy = translating_gaussian_surface_eddy(eddy_times, **eddy_config)

    internal_config = config["internal_wave"]
    internal_interval = internal_config["period_s"] / 32.0
    internal_times = regular_times(64, internal_interval)
    internal = oscillating_compensated_gaussian_dipole(internal_times, **internal_config)

    tsunami_config = config["tsunami"]
    tsunami_speed = math.sqrt(STANDARD_GRAVITY.value * tsunami_config["water_depth_m"])
    tsunami_characteristic_time = tsunami_config["horizontal_scale_m"] / tsunami_speed
    tsunami_interval = tsunami_characteristic_time / 4.0
    tsunami_times = regular_times(
        49, tsunami_interval, start_time_s=-4.0 * tsunami_characteristic_time
    )
    tsunami = propagating_compensated_gaussian_tsunami(tsunami_times, **tsunami_config)

    landslide_config = config["landslide"]
    landslide_interval = landslide_config["transition_duration_s"] / 20.0
    landslide_times = regular_times(
        61,
        landslide_interval,
        start_time_s=-0.5 * landslide_config["transition_duration_s"],
    )
    landslide = mass_conserving_submarine_landslide(landslide_times, **landslide_config)

    return {
        "tide": (tide, tide_interval, {}),
        "storm_surge": (surge, surge_interval, {}),
        "eddy_surface": (eddy, eddy_interval, {}),
        "internal_wave_dipole": (
            internal.signal,
            internal_interval,
            {"net_mass_per_unit_peak_density_m3": internal.net_mass_per_unit_peak_density_m3},
        ),
        "tsunami_packet": (
            tsunami.signal,
            tsunami_interval,
            {
                "phase_speed_m_s": tsunami.shallow_water_phase_speed_m_s,
                "net_surface_mass_amplitude_kg": tsunami.net_surface_mass_amplitude_kg,
            },
        ),
        "submarine_landslide": (
            landslide.signal,
            landslide_interval,
            {
                "net_mass_anomaly_kg": landslide.net_mass_anomaly_kg,
                "final_vertical_gradient_change_s2": landslide.final_gravity_gradient_change_s2[2][
                    2
                ],
            },
        ),
    }


def run(config: dict) -> dict:
    built = build_process_signals(config)
    metrics = {}
    for name, (signal, interval, extras) in built.items():
        process_metrics = _signal_metrics(signal, interval)
        process_metrics.update(extras)
        metrics[name] = process_metrics
    return {
        "schema_version": 1,
        "experiment_id": "P1-E001-foundation",
        "result_class": "engineering_reference_not_cited_physical_prior",
        "config_sha256": hashlib.sha256(
            json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "metrics": metrics,
    }


def main() -> int:
    args = parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    result = run(config)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
