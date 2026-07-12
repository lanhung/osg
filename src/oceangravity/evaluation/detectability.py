"""Band-coverage-aware detectability against an instrument noise curve."""

from __future__ import annotations

import itertools
import math
from collections.abc import Sequence
from dataclasses import dataclass

from oceangravity.instruments import NoiseCurve
from oceangravity.signal_processing import matched_filter_snr, one_sided_spectrum


@dataclass(frozen=True, slots=True)
class CurveDetectabilityResult:
    instrument_id: str
    status: str
    matched_filter_snr_in_covered_band: float | None
    required_expected_snr: float
    signal_energy_coverage_fraction: float
    covered_minimum_frequency_hz: float | None
    covered_maximum_frequency_hz: float | None
    covered_bin_count: int


def evaluate_gravity_signal_against_curve(
    samples_m_s2: Sequence[float],
    sample_interval_s: float,
    curve: NoiseCurve,
    *,
    required_expected_snr: float,
    minimum_signal_energy_coverage: float = 0.9,
    numerical_energy_coverage_floor: float = 0.0,
) -> CurveDetectabilityResult:
    """Classify only when a vertical-gravity curve covers enough signal energy."""

    return _evaluate_signal_against_curve(
        samples_m_s2,
        sample_interval_s,
        curve,
        required_expected_snr=required_expected_snr,
        minimum_signal_energy_coverage=minimum_signal_energy_coverage,
        numerical_energy_coverage_floor=numerical_energy_coverage_floor,
        expected_observable="vertical_gravity",
        expected_asd_unit="m s^-2 Hz^-1/2",
    )


def evaluate_gradient_signal_against_curve(
    samples_s2: Sequence[float],
    sample_interval_s: float,
    curve: NoiseCurve,
    *,
    required_expected_snr: float,
    minimum_signal_energy_coverage: float = 0.9,
    numerical_energy_coverage_floor: float = 0.0,
) -> CurveDetectabilityResult:
    """Classify only when a gravity-gradient curve covers enough signal energy."""

    return _evaluate_signal_against_curve(
        samples_s2,
        sample_interval_s,
        curve,
        required_expected_snr=required_expected_snr,
        minimum_signal_energy_coverage=minimum_signal_energy_coverage,
        numerical_energy_coverage_floor=numerical_energy_coverage_floor,
        expected_observable="gravity_gradient",
        expected_asd_unit="s^-2 Hz^-1/2",
    )


def _evaluate_signal_against_curve(
    samples: Sequence[float],
    sample_interval_s: float,
    curve: NoiseCurve,
    *,
    required_expected_snr: float,
    minimum_signal_energy_coverage: float,
    numerical_energy_coverage_floor: float,
    expected_observable: str,
    expected_asd_unit: str,
) -> CurveDetectabilityResult:
    if curve.observable != expected_observable:
        raise ValueError(f"signal requires a {expected_observable} instrument curve")
    if curve.asd_unit != expected_asd_unit:
        raise ValueError(f"curve ASD unit must be {expected_asd_unit!r}")
    required_snr = float(required_expected_snr)
    coverage_threshold = float(minimum_signal_energy_coverage)
    numerical_floor = float(numerical_energy_coverage_floor)
    if not math.isfinite(required_snr) or required_snr < 0.0:
        raise ValueError("required_expected_snr must be finite and non-negative")
    if not math.isfinite(coverage_threshold) or not 0.0 < coverage_threshold <= 1.0:
        raise ValueError("minimum_signal_energy_coverage must lie in (0, 1]")
    if not math.isfinite(numerical_floor) or not 0.0 <= numerical_floor < coverage_threshold:
        raise ValueError(
            "numerical_energy_coverage_floor must be finite, non-negative, and below "
            "minimum_signal_energy_coverage"
        )

    spectrum = one_sided_spectrum(
        samples,
        sample_interval_s,
        detrend="constant",
    )
    positive_indices = list(range(1, len(spectrum.frequencies_hz)))
    total_energy = _trapezoid_spectral_energy(
        spectrum.frequencies_hz,
        spectrum.fourier_amplitude,
        positive_indices,
    )
    covered_indices = [
        index
        for index in positive_indices
        if curve.frequencies_hz[0] <= spectrum.frequencies_hz[index] <= curve.frequencies_hz[-1]
    ]
    if len(covered_indices) < 2:
        return CurveDetectabilityResult(
            instrument_id=curve.instrument_id,
            status="no_frequency_coverage",
            matched_filter_snr_in_covered_band=None,
            required_expected_snr=required_snr,
            signal_energy_coverage_fraction=0.0,
            covered_minimum_frequency_hz=None,
            covered_maximum_frequency_hz=None,
            covered_bin_count=len(covered_indices),
        )
    if total_energy == 0.0:
        return CurveDetectabilityResult(
            instrument_id=curve.instrument_id,
            status="zero_signal",
            matched_filter_snr_in_covered_band=0.0,
            required_expected_snr=required_snr,
            signal_energy_coverage_fraction=1.0,
            covered_minimum_frequency_hz=spectrum.frequencies_hz[covered_indices[0]],
            covered_maximum_frequency_hz=spectrum.frequencies_hz[covered_indices[-1]],
            covered_bin_count=len(covered_indices),
        )

    covered_energy = _trapezoid_spectral_energy(
        spectrum.frequencies_hz,
        spectrum.fourier_amplitude,
        covered_indices,
    )
    coverage_fraction = min(max(covered_energy / total_energy, 0.0), 1.0)
    frequencies = tuple(spectrum.frequencies_hz[index] for index in covered_indices)
    amplitudes = tuple(spectrum.fourier_amplitude[index] for index in covered_indices)
    noise_psd = tuple(curve.psd_at(frequency) for frequency in frequencies)
    snr = matched_filter_snr(frequencies, amplitudes, noise_psd)
    if coverage_fraction < numerical_floor:
        coverage_fraction = 0.0
        snr = 0.0
    if coverage_fraction < coverage_threshold:
        status = "partial_band_not_classified"
    elif snr >= required_snr:
        status = "detectable_under_curve_model"
    else:
        status = "not_detectable_under_curve_model"
    return CurveDetectabilityResult(
        instrument_id=curve.instrument_id,
        status=status,
        matched_filter_snr_in_covered_band=snr,
        required_expected_snr=required_snr,
        signal_energy_coverage_fraction=coverage_fraction,
        covered_minimum_frequency_hz=frequencies[0],
        covered_maximum_frequency_hz=frequencies[-1],
        covered_bin_count=len(frequencies),
    )


def _trapezoid_spectral_energy(
    frequencies: Sequence[float],
    amplitudes: Sequence[complex],
    indices: Sequence[int],
) -> float:
    if len(indices) < 2:
        return 0.0
    terms = []
    for left, right in itertools.pairwise(indices):
        if right != left + 1:
            raise ValueError("spectral-energy indices must be contiguous")
        width = frequencies[right] - frequencies[left]
        terms.append(0.5 * width * (abs(amplitudes[left]) ** 2 + abs(amplitudes[right]) ** 2))
    return math.fsum(terms)
