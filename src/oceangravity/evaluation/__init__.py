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
from .empirical_detection import (
    EmpiricalThreshold,
    QuietScoreWindow,
    QuietWindowFalsePositiveAudit,
    audit_quiet_window_false_positives,
    calibrate_empirical_threshold,
    empirical_detection_probability,
)
from .time_dependent import (
    DetectionProbabilityPoint,
    earliest_reliable_detection_time,
    time_dependent_detection_probability,
)
from .magnitude import (
    MagnitudePerformancePoint,
    earliest_reliable_magnitude_time,
    time_dependent_magnitude_performance,
)
from .events import (
    EventDataGateAudit,
    EventDesignAudit,
    EventStationData,
    EventWindow,
    audit_event_data_gate,
    audit_event_design,
)
from .case_reproduction import (
    CaseReproductionAudit,
    CaseTarget,
    CaseTargetResult,
    evaluate_case_reproduction,
)
from .event_metrics import (
    EventModelImprovement,
    EventModelMetrics,
    compare_event_model_improvement,
    evaluate_event_model_metrics,
)
from .attribution import (
    OceanAttributionBlockBootstrap,
    OceanAttributionFit,
    bootstrap_ocean_attribution_by_event,
    fit_ocean_attribution_coefficient,
    predict_heldout_ocean_attribution,
)

__all__ = [
    "gaussian_detection_probability",
    "CurveDetectabilityResult",
    "EmpiricalThreshold",
    "QuietScoreWindow",
    "QuietWindowFalsePositiveAudit",
    "DetectionProbabilityPoint",
    "MagnitudePerformancePoint",
    "EventDesignAudit",
    "EventDataGateAudit",
    "EventStationData",
    "EventWindow",
    "CaseReproductionAudit",
    "CaseTarget",
    "CaseTargetResult",
    "evaluate_gravity_signal_against_curve",
    "evaluate_gradient_signal_against_curve",
    "gaussian_threshold_for_false_alarm",
    "calibrate_empirical_threshold",
    "audit_quiet_window_false_positives",
    "audit_event_design",
    "audit_event_data_gate",
    "evaluate_case_reproduction",
    "EventModelMetrics",
    "EventModelImprovement",
    "compare_event_model_improvement",
    "evaluate_event_model_metrics",
    "OceanAttributionFit",
    "OceanAttributionBlockBootstrap",
    "bootstrap_ocean_attribution_by_event",
    "fit_ocean_attribution_coefficient",
    "predict_heldout_ocean_attribution",
    "empirical_detection_probability",
    "earliest_reliable_detection_time",
    "earliest_reliable_magnitude_time",
    "latin_hypercube",
    "ParameterRange",
    "ParameterDesign",
    "ParameterEnvelope",
    "quantile",
    "required_snr_for_detection_probability",
    "summarize_ensemble",
    "sample_parameter_design",
    "time_dependent_detection_probability",
    "time_dependent_magnitude_performance",
]
