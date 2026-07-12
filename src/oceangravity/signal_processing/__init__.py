"""Time/frequency transforms, detection statistics, and signal conditioning."""

from .spectrum import OneSidedSpectrum, mean_square_from_psd, one_sided_spectrum
from .timebase import (
    TimebaseSegmentationResult,
    UniformTimeSeriesSegment,
    split_uniform_time_series,
)
from .quality import TimeSeriesQualitySummary, assess_time_series_quality
from .snr import coherent_periodic_snr, matched_filter_snr

__all__ = [
    "OneSidedSpectrum",
    "coherent_periodic_snr",
    "matched_filter_snr",
    "mean_square_from_psd",
    "one_sided_spectrum",
    "split_uniform_time_series",
    "TimebaseSegmentationResult",
    "UniformTimeSeriesSegment",
    "TimeSeriesQualitySummary",
    "assess_time_series_quality",
]
