"""Spectral-energy coverage requirements for finite real-valued signals."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from itertools import pairwise

from .spectrum import one_sided_spectrum


@dataclass(frozen=True, slots=True)
class LowFrequencyCoverageRequirement:
    """Lowest-band-edge requirement at a fixed upper frequency.

    ``maximum_admissible_low_frequency_hz`` is the highest lower band edge whose
    contiguous band through ``maximum_frequency_hz`` contains at least the
    requested fraction of the complete positive-frequency signal energy. It is
    a coverage requirement, not a detection probability or an SNR threshold.
    """

    required_energy_fraction: float
    maximum_frequency_hz: float
    maximum_admissible_low_frequency_hz: float | None
    achieved_energy_fraction: float
    upper_frequency_sufficient: bool
    positive_frequency_bin_count: int
    covered_bin_count: int


def low_frequency_coverage_requirements(
    samples: Sequence[float],
    sample_interval_s: float,
    required_energy_fractions: Sequence[float],
    *,
    maximum_frequency_hz: float | None = None,
) -> tuple[LowFrequencyCoverageRequirement, ...]:
    """Return band-edge requirements using the project's frozen spectrum convention."""

    thresholds = tuple(float(value) for value in required_energy_fractions)
    if not thresholds or any(
        not math.isfinite(value) or not 0.0 < value <= 1.0 for value in thresholds
    ):
        raise ValueError("required_energy_fractions must contain values in (0, 1]")
    if tuple(sorted(set(thresholds))) != thresholds:
        raise ValueError("required_energy_fractions must be unique and increasing")

    spectrum = one_sided_spectrum(samples, sample_interval_s, detrend="constant")
    frequencies = spectrum.frequencies_hz
    amplitudes = spectrum.fourier_amplitude
    positive = tuple(range(1, len(frequencies)))
    if len(positive) < 2:
        raise ValueError("signal must contain at least two positive-frequency bins")

    upper = frequencies[-1] if maximum_frequency_hz is None else float(maximum_frequency_hz)
    if not math.isfinite(upper) or upper <= 0.0:
        raise ValueError("maximum_frequency_hz must be finite and positive")
    eligible = tuple(index for index in positive if frequencies[index] <= upper)
    total_energy = _contiguous_energy(frequencies, amplitudes, positive)
    if total_energy <= 0.0:
        raise ValueError("positive-frequency signal energy must be greater than zero")

    results = []
    for threshold in thresholds:
        full_band_energy = _contiguous_energy(frequencies, amplitudes, eligible)
        full_fraction = min(max(full_band_energy / total_energy, 0.0), 1.0)
        selected_start = None
        selected_fraction = full_fraction
        if len(eligible) >= 2 and full_fraction >= threshold:
            for position in range(len(eligible) - 1):
                suffix = eligible[position:]
                fraction = min(
                    max(_contiguous_energy(frequencies, amplitudes, suffix) / total_energy, 0.0),
                    1.0,
                )
                if fraction >= threshold:
                    selected_start = position
                    selected_fraction = fraction
                else:
                    break
        results.append(
            LowFrequencyCoverageRequirement(
                required_energy_fraction=threshold,
                maximum_frequency_hz=upper,
                maximum_admissible_low_frequency_hz=(
                    None if selected_start is None else frequencies[eligible[selected_start]]
                ),
                achieved_energy_fraction=selected_fraction,
                upper_frequency_sufficient=selected_start is not None,
                positive_frequency_bin_count=len(positive),
                covered_bin_count=(
                    len(eligible) - selected_start if selected_start is not None else len(eligible)
                ),
            )
        )
    return tuple(results)


def _contiguous_energy(frequencies, amplitudes, indices: Sequence[int]) -> float:
    if len(indices) < 2:
        return 0.0
    return math.fsum(
        0.5
        * (frequencies[right] - frequencies[left])
        * (abs(amplitudes[left]) ** 2 + abs(amplitudes[right]) ** 2)
        for left, right in pairwise(indices)
    )
