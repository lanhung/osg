"""Time/frequency transforms, detection statistics, and signal conditioning."""

from .annotations import (
    DataQualityAnnotation,
    QualityAnnotationResult,
    apply_quality_annotations,
)
from .calibration import CalibratedGravity, GravityCalibration, apply_feedback_calibration
from .coherence import (
    WelchCoherence,
    mean_coherence_in_band,
    welch_magnitude_squared_coherence,
)
from .drift import (
    InstrumentDriftCorrection,
    InstrumentDriftModel,
    apply_instrument_drift_model,
)
from .quality import TimeSeriesQualitySummary, assess_time_series_quality
from .snr import (
    MaskedEventSnr,
    coherent_periodic_snr,
    masked_event_matched_filter_snr,
    matched_filter_snr,
)
from .spectrum import OneSidedSpectrum, mean_square_from_psd, one_sided_spectrum
from .steps import (
    InstrumentStepCorrection,
    InstrumentStepDecision,
    apply_instrument_step_decisions,
)
from .timebase import (
    TimebaseSegmentationResult,
    UniformTimeSeriesSegment,
    split_uniform_time_series,
)

__all__ = [
    "CalibratedGravity",
    "DataQualityAnnotation",
    "GravityCalibration",
    "InstrumentDriftCorrection",
    "InstrumentDriftModel",
    "InstrumentStepCorrection",
    "InstrumentStepDecision",
    "MaskedEventSnr",
    "OneSidedSpectrum",
    "QualityAnnotationResult",
    "TimeSeriesQualitySummary",
    "TimebaseSegmentationResult",
    "UniformTimeSeriesSegment",
    "WelchCoherence",
    "apply_feedback_calibration",
    "apply_instrument_drift_model",
    "apply_instrument_step_decisions",
    "apply_quality_annotations",
    "assess_time_series_quality",
    "coherent_periodic_snr",
    "masked_event_matched_filter_snr",
    "matched_filter_snr",
    "mean_coherence_in_band",
    "mean_square_from_psd",
    "one_sided_spectrum",
    "split_uniform_time_series",
    "welch_magnitude_squared_coherence",
]
