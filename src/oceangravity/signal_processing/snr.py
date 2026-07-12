"""Reference signal-to-noise ratios under explicit one-sided PSD conventions."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from .spectrum import one_sided_spectrum


@dataclass(frozen=True, slots=True)
class MaskedEventSnr:
    matched_filter_snr: float
    segment_snrs: tuple[float, ...]
    used_segment_starts: tuple[int, ...]
    discarded_segment_starts: tuple[int, ...]
    segment_length_samples: int
    trailing_unsegmented_samples: int
    included_sample_count: int
    sample_interval_s: float
    detrend: str
    window: str
    minimum_frequency_hz: float | None
    maximum_frequency_hz: float | None


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


def masked_event_matched_filter_snr(
    signal_samples: Sequence[float],
    sample_interval_s: float,
    noise_one_sided_psd: Sequence[float],
    *,
    segment_length_samples: int,
    inclusion_mask: Sequence[bool] | None = None,
    minimum_frequency_hz: float | None = None,
    maximum_frequency_hz: float | None = None,
    detrend: str = "none",
    window: str = "rectangular",
) -> MaskedEventSnr:
    """Combine non-overlapping, fully included segment SNRs in quadrature."""

    samples = tuple(float(value) for value in signal_samples)
    if not samples or not all(math.isfinite(value) for value in samples):
        raise ValueError("event signal samples must be non-empty and finite")
    if isinstance(segment_length_samples, bool) or not isinstance(
        segment_length_samples, int
    ) or segment_length_samples < 4:
        raise ValueError("segment_length_samples must be an integer >= 4")
    if len(samples) < segment_length_samples:
        raise ValueError("event signal is shorter than one SNR segment")
    if inclusion_mask is None:
        mask = (True,) * len(samples)
    else:
        mask = tuple(inclusion_mask)
        if len(mask) != len(samples) or any(not isinstance(value, bool) for value in mask):
            raise ValueError("event SNR inclusion mask must contain one boolean per sample")

    complete_sample_count = (len(samples) // segment_length_samples) * segment_length_samples
    candidate_starts = tuple(range(0, complete_sample_count, segment_length_samples))
    used = tuple(
        start
        for start in candidate_starts
        if all(mask[start : start + segment_length_samples])
    )
    used_set = set(used)
    discarded = tuple(start for start in candidate_starts if start not in used_set)
    if not used:
        raise ValueError("event SNR requires at least one fully included segment")

    segment_snrs = []
    for start in used:
        spectrum = one_sided_spectrum(
            samples[start : start + segment_length_samples],
            sample_interval_s,
            detrend=detrend,
            window=window,
        )
        segment_snrs.append(
            matched_filter_snr(
                spectrum.frequencies_hz,
                spectrum.fourier_amplitude,
                noise_one_sided_psd,
                minimum_frequency_hz=minimum_frequency_hz,
                maximum_frequency_hz=maximum_frequency_hz,
            )
        )
    return MaskedEventSnr(
        matched_filter_snr=math.sqrt(math.fsum(value * value for value in segment_snrs)),
        segment_snrs=tuple(segment_snrs),
        used_segment_starts=used,
        discarded_segment_starts=discarded,
        segment_length_samples=segment_length_samples,
        trailing_unsegmented_samples=len(samples) - complete_sample_count,
        included_sample_count=len(used) * segment_length_samples,
        sample_interval_s=float(sample_interval_s),
        detrend=detrend,
        window=window,
        minimum_frequency_hz=minimum_frequency_hz,
        maximum_frequency_hz=maximum_frequency_hz,
    )
