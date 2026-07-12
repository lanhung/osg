"""Dependency-free reference Fourier and one-sided PSD conventions."""

from __future__ import annotations

import cmath
import math
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OneSidedSpectrum:
    """Reference spectrum for a finite real-valued time series.

    ``fourier_amplitude`` approximates the continuous transform
    ``X(f) = integral x(t) exp(-2 pi i f t) dt`` and therefore has units of input
    units times seconds. ``power_spectral_density`` is the one-sided periodogram
    ``weight * |X|^2 / T`` and has units of input-units squared per hertz.
    """

    frequencies_hz: tuple[float, ...]
    fourier_amplitude: tuple[complex, ...]
    power_spectral_density: tuple[float, ...]
    sample_interval_s: float
    duration_s: float
    frequency_spacing_hz: float
    removed_mean: float
    removed_linear_slope_per_s: float
    detrend: str
    window: str
    window_coherent_gain: float
    window_power_gain: float
    equivalent_noise_bandwidth_bins: float


def one_sided_spectrum(
    samples: Sequence[float],
    sample_interval_s: float,
    *,
    remove_mean: bool = False,
    detrend: str = "none",
    window: str = "rectangular",
) -> OneSidedSpectrum:
    """Compute a transparent O(N^2) reference DFT and one-sided periodogram.

    This implementation exists to lock normalization and tests. Production arrays
    will use an FFT backend that must reproduce these results within tolerance.
    The record duration is ``N * sample_interval_s``. PSD normalization divides
    by window power gain, so its integral is the normalized window-weighted mean
    square. ``remove_mean=True`` is a backward-compatible alias for constant
    detrending and cannot be combined with an explicit detrend choice.
    """

    sample_count = len(samples)
    if sample_count < 2:
        raise ValueError("samples must contain at least two values")
    interval = float(sample_interval_s)
    if not math.isfinite(interval) or interval <= 0.0:
        raise ValueError("sample_interval_s must be finite and greater than zero")
    values = tuple(float(value) for value in samples)
    if not all(math.isfinite(value) for value in values):
        raise ValueError("samples must contain only finite values")

    if remove_mean:
        if detrend != "none":
            raise ValueError("remove_mean cannot be combined with explicit detrend")
        detrend = "constant"
    centred, mean, slope = _detrend(values, interval, detrend)
    window_values = _window(sample_count, window)
    coherent_gain = math.fsum(window_values) / sample_count
    power_gain = math.fsum(value * value for value in window_values) / sample_count
    equivalent_noise_bandwidth = power_gain / coherent_gain**2
    weighted = tuple(centred[index] * window_values[index] for index in range(sample_count))
    duration = sample_count * interval
    frequency_spacing = 1.0 / duration
    highest_bin = sample_count // 2
    amplitudes: list[complex] = []
    psd: list[float] = []
    for frequency_index in range(highest_bin + 1):
        terms = (
            weighted[time_index]
            * cmath.exp(-2j * math.pi * frequency_index * time_index / sample_count)
            for time_index in range(sample_count)
        )
        amplitude = interval * sum(terms, 0j)
        is_dc = frequency_index == 0
        is_nyquist = sample_count % 2 == 0 and frequency_index == highest_bin
        one_sided_weight = 1.0 if is_dc or is_nyquist else 2.0
        amplitudes.append(amplitude)
        psd.append(one_sided_weight * abs(amplitude) ** 2 / (duration * power_gain))

    return OneSidedSpectrum(
        frequencies_hz=tuple(index * frequency_spacing for index in range(highest_bin + 1)),
        fourier_amplitude=tuple(amplitudes),
        power_spectral_density=tuple(psd),
        sample_interval_s=interval,
        duration_s=duration,
        frequency_spacing_hz=frequency_spacing,
        removed_mean=mean,
        removed_linear_slope_per_s=slope,
        detrend=detrend,
        window=window,
        window_coherent_gain=coherent_gain,
        window_power_gain=power_gain,
        equivalent_noise_bandwidth_bins=equivalent_noise_bandwidth,
    )


def mean_square_from_psd(spectrum: OneSidedSpectrum) -> float:
    """Integrate the one-sided periodogram to recover record mean square."""

    return math.fsum(spectrum.power_spectral_density) * spectrum.frequency_spacing_hz


def _detrend(
    values: tuple[float, ...], interval: float, method: str
) -> tuple[tuple[float, ...], float, float]:
    if method not in {"none", "constant", "linear"}:
        raise ValueError("detrend must be 'none', 'constant', or 'linear'")
    if method == "none":
        return values, 0.0, 0.0
    mean = math.fsum(values) / len(values)
    if method == "constant":
        return tuple(value - mean for value in values), mean, 0.0

    midpoint = 0.5 * (len(values) - 1) * interval
    centred_times = tuple(index * interval - midpoint for index in range(len(values)))
    denominator = math.fsum(time * time for time in centred_times)
    slope = (
        math.fsum(centred_times[index] * (values[index] - mean) for index in range(len(values)))
        / denominator
    )
    residual = tuple(
        values[index] - mean - slope * centred_times[index] for index in range(len(values))
    )
    return residual, mean, slope


def _window(sample_count: int, name: str) -> tuple[float, ...]:
    if name == "rectangular":
        return (1.0,) * sample_count
    if name == "hann-periodic":
        return tuple(
            0.5 - 0.5 * math.cos(2.0 * math.pi * index / sample_count)
            for index in range(sample_count)
        )
    raise ValueError("window must be 'rectangular' or 'hann-periodic'")
