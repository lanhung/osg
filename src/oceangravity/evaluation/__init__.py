"""Metrics, uncertainty, holdout evaluation, and experiment reporting."""

from .attribution import (
    OceanAttributionBlockBootstrap,
    OceanAttributionFit,
    bootstrap_ocean_attribution_by_event,
    fit_ocean_attribution_coefficient,
    predict_heldout_ocean_attribution,
)
from .canonical import canonicalize_report_floats
from .case_reproduction import (
    CaseReproductionAudit,
    CaseTarget,
    CaseTargetResult,
    evaluate_case_reproduction,
)
from .detectability import (
    CurveDetectabilityResult,
    evaluate_gradient_signal_against_curve,
    evaluate_gravity_signal_against_curve,
)
from .detection import (
    gaussian_detection_probability,
    gaussian_threshold_for_false_alarm,
    required_snr_for_detection_probability,
)
from .empirical_detection import (
    EmpiricalThreshold,
    QuietScoreWindow,
    QuietWindowFalsePositiveAudit,
    audit_quiet_window_false_positives,
    calibrate_empirical_threshold,
    empirical_detection_probability,
)
from .event_metrics import (
    EventModelImprovement,
    EventModelMetrics,
    compare_event_model_improvement,
    evaluate_event_model_metrics,
)
from .events import (
    EventDataGateAudit,
    EventDesignAudit,
    EventStationData,
    EventWindow,
    audit_event_data_gate,
    audit_event_design,
)
from .magnitude import (
    MagnitudePerformancePoint,
    earliest_reliable_magnitude_time,
    time_dependent_magnitude_performance,
)
from .paper2_decision import (
    Paper2DecisionAudit,
    Paper2DecisionEvidence,
    Paper2NoveltyAudit,
    audit_paper2_decision,
)
from .priors import ParameterDesign, ParameterEnvelope, sample_parameter_design
from .sampling import ParameterRange, latin_hypercube, quantile, summarize_ensemble
from .time_dependent import (
    DetectionProbabilityPoint,
    earliest_reliable_detection_time,
    time_dependent_detection_probability,
)

__all__ = [
    "CaseReproductionAudit",
    "CaseTarget",
    "CaseTargetResult",
    "CurveDetectabilityResult",
    "DetectionProbabilityPoint",
    "EmpiricalThreshold",
    "EventDataGateAudit",
    "EventDesignAudit",
    "EventModelImprovement",
    "EventModelMetrics",
    "EventStationData",
    "EventWindow",
    "MagnitudePerformancePoint",
    "OceanAttributionBlockBootstrap",
    "OceanAttributionFit",
    "Paper2DecisionAudit",
    "Paper2DecisionEvidence",
    "Paper2NoveltyAudit",
    "ParameterDesign",
    "ParameterEnvelope",
    "ParameterRange",
    "QuietScoreWindow",
    "QuietWindowFalsePositiveAudit",
    "audit_event_data_gate",
    "audit_event_design",
    "audit_paper2_decision",
    "audit_quiet_window_false_positives",
    "bootstrap_ocean_attribution_by_event",
    "calibrate_empirical_threshold",
    "canonicalize_report_floats",
    "compare_event_model_improvement",
    "earliest_reliable_detection_time",
    "earliest_reliable_magnitude_time",
    "empirical_detection_probability",
    "evaluate_case_reproduction",
    "evaluate_event_model_metrics",
    "evaluate_gradient_signal_against_curve",
    "evaluate_gravity_signal_against_curve",
    "fit_ocean_attribution_coefficient",
    "gaussian_detection_probability",
    "gaussian_threshold_for_false_alarm",
    "latin_hypercube",
    "predict_heldout_ocean_attribution",
    "quantile",
    "required_snr_for_detection_probability",
    "sample_parameter_design",
    "summarize_ensemble",
    "time_dependent_detection_probability",
    "time_dependent_magnitude_performance",
]
