"""Reference signal-to-noise ratios under explicit one-sided PSD conventions."""

from __future__ import annotations

import math
from collections.abc import Sequence


def matched_filter_snr(
    frequencies_hz: Sequence[float],
    signal_fourier_amplitude: Sequence[complex],
    noise_one_sided_psd: Sequence[float],
    *,
    minimum_frequency_hz: float | None = None,
    maximum_frequency_hz: float | None = None,
) -> float:
    """Compute ``rho^2 = 4 integral |s_tilde|^2 / S_n df`` by trapezoids.

    Frequencies must be strictly increasing. Noise PSD is one-sided and positive,
    with units matching signal-units squared per hertz. By default DC is excluded
    and all strictly positive sampled frequencies are used. Requested band edges
    select existing bins; no unrecorded boundary value is invented by interpolation.
    """

    count = len(frequencies_hz)
    if len(signal_fourier_amplitude) != count or len(noise_one_sided_psd) != count:
        raise ValueError("frequency, signal, and noise arrays must have equal length")
    if count < 2:
        raise ValueError("at least two frequency bins are required")
    frequencies = tuple(float(value) for value in frequencies_hz)
    if not all(math.isfinite(value) and value >= 0.0 for value in frequencies):
        raise ValueError("frequencies must be finite and non-negative")
    if any(frequencies[index + 1] <= frequencies[index] for index in range(count - 1)):
        raise ValueError("frequencies must be strictly increasing")

    signals = tuple(complex(value) for value in signal_fourier_amplitude)
    if not all(math.isfinite(value.real) and math.isfinite(value.imag) for value in signals):
        raise ValueError("signal Fourier amplitudes must be finite")
    noise = tuple(float(value) for value in noise_one_sided_psd)
    if not all(math.isfinite(value) and value > 0.0 for value in noise):
        raise ValueError("noise one-sided PSD must be finite and greater than zero")

    default_minimum = next((value for value in frequencies if value > 0.0), frequencies[-1])
    minimum = default_minimum if minimum_frequency_hz is None else float(minimum_frequency_hz)
    maximum = frequencies[-1] if maximum_frequency_hz is None else float(maximum_frequency_hz)
    if not math.isfinite(minimum) or not math.isfinite(maximum):
        raise ValueError("frequency bounds must be finite")
    if minimum < 0.0 or maximum < minimum:
        raise ValueError("frequency bounds must satisfy 0 <= minimum <= maximum")

    selected = [
        index for index, frequency in enumerate(frequencies) if minimum <= frequency <= maximum
    ]
    if len(selected) < 2:
        raise ValueError("selected band must contain at least two sampled frequency bins")
    integrand = tuple(4.0 * abs(signals[index]) ** 2 / noise[index] for index in range(count))
    integral_terms = []
    for left, right in zip(selected[:-1], selected[1:], strict=True):
        if right != left + 1:
            raise ValueError("selected frequency band must be contiguous")
        width = frequencies[right] - frequencies[left]
        integral_terms.append(0.5 * width * (integrand[left] + integrand[right]))
    snr_squared = math.fsum(integral_terms)
    return math.sqrt(max(snr_squared, 0.0))


def coherent_periodic_snr(
    peak_amplitude: float,
    noise_one_sided_psd_at_signal: float,
    observation_time_s: float,
    *,
    coherent_fraction: float = 1.0,
) -> float:
    """Return coherent SNR for a sinusoid with stated *peak* amplitude.

    Under the same convention as :func:`matched_filter_snr`, an exactly modelled
    sinusoid has ``rho = |A_peak| sqrt(T_coherent / S_n)``. ``coherent_fraction``
    reduces usable integration time and must lie in ``(0, 1]``.
    """

    amplitude = float(peak_amplitude)
    noise = float(noise_one_sided_psd_at_signal)
    duration = float(observation_time_s)
    fraction = float(coherent_fraction)
    for name, value in (
        ("peak_amplitude", amplitude),
        ("noise_one_sided_psd_at_signal", noise),
        ("observation_time_s", duration),
        ("coherent_fraction", fraction),
    ):
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")
    if noise <= 0.0:
        raise ValueError("noise_one_sided_psd_at_signal must be greater than zero")
    if duration <= 0.0:
        raise ValueError("observation_time_s must be greater than zero")
    if not 0.0 < fraction <= 1.0:
        raise ValueError("coherent_fraction must lie in (0, 1]")
    return abs(amplitude) * math.sqrt(duration * fraction / noise)

