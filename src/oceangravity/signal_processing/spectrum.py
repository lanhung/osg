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


def one_sided_spectrum(
    samples: Sequence[float],
    sample_interval_s: float,
    *,
    remove_mean: bool = False,
) -> OneSidedSpectrum:
    """Compute a transparent O(N^2) reference DFT and one-sided periodogram.

    This implementation exists to lock normalization and tests. Production arrays
    will use an FFT backend that must reproduce these results within tolerance.
    No window is applied. The record duration is ``N * sample_interval_s``.
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

    mean = math.fsum(values) / sample_count if remove_mean else 0.0
    centred = tuple(value - mean for value in values)
    duration = sample_count * interval
    frequency_spacing = 1.0 / duration
    highest_bin = sample_count // 2
    amplitudes: list[complex] = []
    psd: list[float] = []
    for frequency_index in range(highest_bin + 1):
        terms = (
            centred[time_index]
            * cmath.exp(-2j * math.pi * frequency_index * time_index / sample_count)
            for time_index in range(sample_count)
        )
        amplitude = interval * sum(terms, 0j)
        is_dc = frequency_index == 0
        is_nyquist = sample_count % 2 == 0 and frequency_index == highest_bin
        one_sided_weight = 1.0 if is_dc or is_nyquist else 2.0
        amplitudes.append(amplitude)
        psd.append(one_sided_weight * abs(amplitude) ** 2 / duration)

    return OneSidedSpectrum(
        frequencies_hz=tuple(index * frequency_spacing for index in range(highest_bin + 1)),
        fourier_amplitude=tuple(amplitudes),
        power_spectral_density=tuple(psd),
        sample_interval_s=interval,
        duration_s=duration,
        frequency_spacing_hz=frequency_spacing,
        removed_mean=mean,
    )


def mean_square_from_psd(spectrum: OneSidedSpectrum) -> float:
    """Integrate the one-sided periodogram to recover record mean square."""

    return math.fsum(spectrum.power_spectral_density) * spectrum.frequency_spacing_hz

