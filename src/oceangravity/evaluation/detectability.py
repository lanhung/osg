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


@dataclass(frozen=True, slots=True)
class FrequencySupportAudit:
    """Numerical common-support diagnostics without a detectability claim."""

    status: str
    record_duration_s: float
    native_frequency_spacing_hz: float
    source_nyquist_hz: float
    instrument_low_edge_hz: float
    instrument_high_edge_hz: float
    common_support_low_hz: float | None
    common_support_high_hz: float | None
    native_overlap_bin_count: int
    resolution_limited: bool


def audit_curve_frequency_support(
    sample_count: int,
    sample_interval_s: float,
    curve: NoiseCurve,
) -> FrequencySupportAudit:
    """Separate source sampling support from published curve support.

    This audit does not inspect signal amplitudes. In particular, fewer than two
    native Fourier bins is reported as a numerical-resolution limitation rather
    than as zero signal energy or absent instrument evidence.
    """

    if isinstance(sample_count, bool) or not isinstance(sample_count, int) or sample_count < 2:
        raise ValueError("sample_count must be an integer of at least two")
    interval = float(sample_interval_s)
    if not math.isfinite(interval) or interval <= 0.0:
        raise ValueError("sample_interval_s must be finite and positive")
    duration = sample_count * interval
    spacing = 1.0 / duration
    nyquist = (sample_count // 2) * spacing
    curve_low = curve.frequencies_hz[0]
    curve_high = curve.frequencies_hz[-1]
    common_low = max(spacing, curve_low)
    common_high = min(nyquist, curve_high)
    if nyquist < curve_low:
        status = "source_temporal_support_below_curve"
        common_low_output = None
        common_high_output = None
        bin_count = 0
    elif curve_high < spacing:
        status = "curve_temporal_support_below_source_resolution"
        common_low_output = None
        common_high_output = None
        bin_count = 0
    else:
        first = max(1, math.ceil(curve_low / spacing - 1.0e-12))
        last = min(sample_count // 2, math.floor(curve_high / spacing + 1.0e-12))
        bin_count = max(0, last - first + 1)
        common_low_output = common_low
        common_high_output = common_high
        status = (
            "common_support_unresolved_by_native_grid"
            if bin_count < 2
            else "native_common_support_resolved"
        )
    return FrequencySupportAudit(
        status=status,
        record_duration_s=duration,
        native_frequency_spacing_hz=spacing,
        source_nyquist_hz=nyquist,
        instrument_low_edge_hz=curve_low,
        instrument_high_edge_hz=curve_high,
        common_support_low_hz=common_low_output,
        common_support_high_hz=common_high_output,
        native_overlap_bin_count=bin_count,
        resolution_limited=status != "native_common_support_resolved",
    )


def boundary_aware_spectral_energy(
    frequencies_hz: Sequence[float],
    amplitudes: Sequence[complex],
    lower_frequency_hz: float,
    upper_frequency_hz: float,
) -> float:
    """Integrate ``|X(f)|^2`` with linearly interpolated band boundaries."""

    if len(frequencies_hz) != len(amplitudes) or len(frequencies_hz) < 2:
        raise ValueError("frequencies and amplitudes must have equal length of at least two")
    frequencies = tuple(float(value) for value in frequencies_hz)
    if any(right <= left for left, right in itertools.pairwise(frequencies)):
        raise ValueError("frequencies must be strictly increasing")
    lower = max(float(lower_frequency_hz), frequencies[0])
    upper = min(float(upper_frequency_hz), frequencies[-1])
    if not math.isfinite(lower) or not math.isfinite(upper) or upper <= lower:
        return 0.0
    powers = tuple(abs(value) ** 2 for value in amplitudes)

    def interpolate(frequency: float) -> float:
        for index, (left, right) in enumerate(itertools.pairwise(frequencies)):
            if left <= frequency <= right:
                fraction = (frequency - left) / (right - left)
                return powers[index] + fraction * (powers[index + 1] - powers[index])
        raise RuntimeError("clamped boundary is outside the frequency grid")

    grid_frequencies = [lower]
    grid_powers = [interpolate(lower)]
    for frequency, power in zip(frequencies, powers, strict=True):
        if lower < frequency < upper:
            grid_frequencies.append(frequency)
            grid_powers.append(power)
    grid_frequencies.append(upper)
    grid_powers.append(interpolate(upper))
    return math.fsum(
        0.5 * (right_f - left_f) * (left_p + right_p)
        for left_f, right_f, left_p, right_p in zip(
            grid_frequencies[:-1],
            grid_frequencies[1:],
            grid_powers[:-1],
            grid_powers[1:],
            strict=True,
        )
    )


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
