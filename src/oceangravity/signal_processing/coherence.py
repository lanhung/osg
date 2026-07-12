"""Dependency-free Welch magnitude-squared coherence with mask-aware segments."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from .spectrum import one_sided_spectrum


@dataclass(frozen=True, slots=True)
class WelchCoherence:
    frequencies_hz: tuple[float, ...]
    magnitude_squared_coherence: tuple[float | None, ...]
    segment_length_samples: int
    overlap_samples: int
    used_segment_starts: tuple[int, ...]
    discarded_segment_starts: tuple[int, ...]
    sample_interval_s: float
    detrend: str
    window: str


def welch_magnitude_squared_coherence(
    first: Sequence[float],
    second: Sequence[float],
    sample_interval_s: float,
    *,
    segment_length_samples: int,
    overlap_samples: int,
    inclusion_mask: Sequence[bool] | None = None,
    detrend: str = "constant",
    window: str = "hann-periodic",
) -> WelchCoherence:
    """Average auto/cross periodograms over fully included complete segments."""

    x = tuple(float(value) for value in first)
    y = tuple(float(value) for value in second)
    if not x or len(x) != len(y):
        raise ValueError("coherence series must have equal nonzero length")
    if not all(math.isfinite(value) for value in (*x, *y)):
        raise ValueError("coherence series must be finite")
    if (
        isinstance(segment_length_samples, bool)
        or not isinstance(segment_length_samples, int)
        or segment_length_samples < 4
    ):
        raise ValueError("segment_length_samples must be an integer >= 4")
    if isinstance(overlap_samples, bool) or not isinstance(overlap_samples, int):
        raise ValueError("overlap_samples must be an integer")
    if not 0 <= overlap_samples < segment_length_samples:
        raise ValueError("overlap_samples must lie in [0, segment length)")
    if len(x) < segment_length_samples:
        raise ValueError("record is shorter than one coherence segment")
    if inclusion_mask is None:
        mask = (True,) * len(x)
    else:
        mask = tuple(inclusion_mask)
        if len(mask) != len(x) or any(not isinstance(value, bool) for value in mask):
            raise ValueError("coherence inclusion mask must contain one boolean per sample")

    step = segment_length_samples - overlap_samples
    candidate_starts = tuple(range(0, len(x) - segment_length_samples + 1, step))
    used = tuple(
        start for start in candidate_starts if all(mask[start : start + segment_length_samples])
    )
    discarded = tuple(start for start in candidate_starts if start not in set(used))
    if len(used) < 2:
        raise ValueError("Welch coherence requires at least two fully included segments")

    x_spectra = []
    y_spectra = []
    for start in used:
        stop = start + segment_length_samples
        x_spectra.append(
            one_sided_spectrum(
                x[start:stop],
                sample_interval_s,
                detrend=detrend,
                window=window,
            )
        )
        y_spectra.append(
            one_sided_spectrum(
                y[start:stop],
                sample_interval_s,
                detrend=detrend,
                window=window,
            )
        )
    frequencies = x_spectra[0].frequencies_hz
    coherence = []
    for frequency_index in range(len(frequencies)):
        first_amplitudes = tuple(
            spectrum.fourier_amplitude[frequency_index] for spectrum in x_spectra
        )
        second_amplitudes = tuple(
            spectrum.fourier_amplitude[frequency_index] for spectrum in y_spectra
        )
        auto_first = math.fsum(abs(value) ** 2 for value in first_amplitudes) / len(used)
        auto_second = math.fsum(abs(value) ** 2 for value in second_amplitudes) / len(used)
        cross = sum(
            (
                first_value * second_value.conjugate()
                for first_value, second_value in zip(
                    first_amplitudes, second_amplitudes, strict=True
                )
            ),
            0j,
        ) / len(used)
        if auto_first == 0.0 or auto_second == 0.0:
            coherence.append(None)
        else:
            value = abs(cross) ** 2 / (auto_first * auto_second)
            coherence.append(min(1.0, max(0.0, value)))
    return WelchCoherence(
        frequencies_hz=frequencies,
        magnitude_squared_coherence=tuple(coherence),
        segment_length_samples=segment_length_samples,
        overlap_samples=overlap_samples,
        used_segment_starts=used,
        discarded_segment_starts=discarded,
        sample_interval_s=float(sample_interval_s),
        detrend=detrend,
        window=window,
    )


def mean_coherence_in_band(
    spectrum: WelchCoherence,
    minimum_frequency_hz: float,
    maximum_frequency_hz: float,
) -> float:
    """Return the unweighted mean of defined bins in a closed frequency band."""

    lower = float(minimum_frequency_hz)
    upper = float(maximum_frequency_hz)
    if not math.isfinite(lower) or not math.isfinite(upper) or lower < 0.0 or lower >= upper:
        raise ValueError("frequency band must be finite, nonnegative, and ordered")
    values = tuple(
        coherence
        for frequency, coherence in zip(
            spectrum.frequencies_hz,
            spectrum.magnitude_squared_coherence,
            strict=True,
        )
        if lower <= frequency <= upper and coherence is not None
    )
    if not values:
        raise ValueError("frequency band contains no defined coherence bins")
    return math.fsum(values) / len(values)
