"""Time/frequency transforms, detection statistics, and signal conditioning."""

from .spectrum import OneSidedSpectrum, mean_square_from_psd, one_sided_spectrum
from .timebase import (
    TimebaseSegmentationResult,
    UniformTimeSeriesSegment,
    split_uniform_time_series,
)
from .quality import TimeSeriesQualitySummary, assess_time_series_quality
from .snr import coherent_periodic_snr, matched_filter_snr
from .calibration import CalibratedGravity, GravityCalibration, apply_feedback_calibration
from .steps import (
    InstrumentStepCorrection,
    InstrumentStepDecision,
    apply_instrument_step_decisions,
)
from .drift import (
    InstrumentDriftCorrection,
    InstrumentDriftModel,
    apply_instrument_drift_model,
)
from .annotations import (
    DataQualityAnnotation,
    QualityAnnotationResult,
    apply_quality_annotations,
)

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
    "CalibratedGravity",
    "GravityCalibration",
    "apply_feedback_calibration",
    "InstrumentStepCorrection",
    "InstrumentStepDecision",
    "apply_instrument_step_decisions",
    "InstrumentDriftCorrection",
    "InstrumentDriftModel",
    "apply_instrument_drift_model",
    "DataQualityAnnotation",
    "QualityAnnotationResult",
    "apply_quality_annotations",
]
