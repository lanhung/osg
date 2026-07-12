"""Metrics, uncertainty, holdout evaluation, and experiment reporting."""

from .detection import (
    gaussian_detection_probability,
    gaussian_threshold_for_false_alarm,
    required_snr_for_detection_probability,
)
from .detectability import (
    CurveDetectabilityResult,
    evaluate_gradient_signal_against_curve,
    evaluate_gravity_signal_against_curve,
)
from .sampling import ParameterRange, latin_hypercube, quantile, summarize_ensemble
from .priors import ParameterDesign, ParameterEnvelope, sample_parameter_design

__all__ = [
    "gaussian_detection_probability",
    "CurveDetectabilityResult",
    "evaluate_gravity_signal_against_curve",
    "evaluate_gradient_signal_against_curve",
    "gaussian_threshold_for_false_alarm",
    "latin_hypercube",
    "ParameterRange",
    "ParameterDesign",
    "ParameterEnvelope",
    "quantile",
    "required_snr_for_detection_probability",
    "summarize_ensemble",
    "sample_parameter_design",
]
