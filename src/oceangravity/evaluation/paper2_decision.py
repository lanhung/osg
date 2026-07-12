"""Claim-safe Paper 2 manuscript-branch decision audit."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Paper2DecisionEvidence:
    uses_real_observations: bool
    data_gate_passes: bool
    analysis_complete: bool
    typhoon_event_count: int
    heldout_event_count: int
    quiet_window_count: int
    effect_closure_ready: bool
    direct_deformation_separated: bool
    multi_source_validation_complete: bool
    sensitivity_analysis_complete: bool
    failed_event_log_complete: bool
    data_license_review_complete: bool
    ocean_coefficient_confidence_interval: tuple[float, float] | None
    heldout_improvement_passes: tuple[bool, ...]
    heldout_quiet_far_passes: bool | None
    event_snrs: tuple[float, ...]
    minimum_interpretable_event_snr: float

    def __post_init__(self) -> None:
        boolean_fields = (
            self.uses_real_observations,
            self.data_gate_passes,
            self.analysis_complete,
            self.effect_closure_ready,
            self.direct_deformation_separated,
            self.multi_source_validation_complete,
            self.sensitivity_analysis_complete,
            self.failed_event_log_complete,
            self.data_license_review_complete,
        )
        if any(not isinstance(value, bool) for value in boolean_fields):
            raise ValueError("Paper 2 decision flags must be boolean")
        counts = (
            self.typhoon_event_count,
            self.heldout_event_count,
            self.quiet_window_count,
        )
        if any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in counts):
            raise ValueError("Paper 2 event/window counts must be non-negative integers")
        if self.heldout_event_count > self.typhoon_event_count:
            raise ValueError("held-out event count cannot exceed typhoon event count")
        if any(not isinstance(value, bool) for value in self.heldout_improvement_passes):
            raise ValueError("held-out improvement results must be boolean")
        if len(self.heldout_improvement_passes) > self.heldout_event_count:
            raise ValueError("held-out improvement results exceed declared held-out events")
        if self.heldout_quiet_far_passes is not None and not isinstance(
            self.heldout_quiet_far_passes, bool
        ):
            raise ValueError("held-out quiet FAR result must be boolean or None")
        if self.ocean_coefficient_confidence_interval is not None:
            lower, upper = self.ocean_coefficient_confidence_interval
            if not all(math.isfinite(value) for value in (lower, upper)) or lower > upper:
                raise ValueError("ocean coefficient confidence interval must be finite and ordered")
        if len(self.event_snrs) > self.typhoon_event_count:
            raise ValueError("event SNR results exceed declared typhoon events")
        if not all(math.isfinite(value) and value >= 0.0 for value in self.event_snrs):
            raise ValueError("event SNR values must be finite and non-negative")
        threshold = self.minimum_interpretable_event_snr
        if not math.isfinite(threshold) or threshold <= 0.0:
            raise ValueError("minimum interpretable event SNR must be finite and positive")


@dataclass(frozen=True, slots=True)
class Paper2DecisionAudit:
    branch: str
    full_attribution_claim_ready: bool
    manuscript_release_ready: bool
    novelty_requirement_count: int
    novelty_requirements: tuple[tuple[str, bool], ...]
    gates: tuple[tuple[str, bool], ...]
    blocking_reasons: tuple[str, ...]
    event_snr_count: int
    event_snr_minimum: float | None
    event_snr_maximum: float | None


def audit_paper2_decision(evidence: Paper2DecisionEvidence) -> Paper2DecisionAudit:
    """Choose a preregistered manuscript branch without inferring missing evidence."""

    coefficient_positive = (
        evidence.ocean_coefficient_confidence_interval is not None
        and evidence.ocean_coefficient_confidence_interval[0] > 0.0
    )
    heldout_results_complete = (
        evidence.heldout_event_count > 0
        and len(evidence.heldout_improvement_passes) == evidence.heldout_event_count
    )
    heldout_improvement_passes = heldout_results_complete and all(
        evidence.heldout_improvement_passes
    )
    multi_event_design = (
        evidence.typhoon_event_count >= 3
        and evidence.heldout_event_count >= 1
        and evidence.quiet_window_count >= 3
    )
    event_snrs_complete = (
        evidence.typhoon_event_count > 0
        and len(evidence.event_snrs) == evidence.typhoon_event_count
    )
    novelty = (
        ("typhoon_event_attribution", coefficient_positive),
        (
            "direct_gravity_and_deformation_separation",
            evidence.direct_deformation_separated and evidence.effect_closure_ready,
        ),
        ("multi_source_closed_loop_validation", evidence.multi_source_validation_complete),
        ("heldout_cross_typhoon_generalization", multi_event_design and heldout_improvement_passes),
    )
    novelty_count = sum(passes for _, passes in novelty)
    gates = (
        ("real_observations", evidence.uses_real_observations),
        ("event_station_data", evidence.data_gate_passes),
        ("analysis_complete", evidence.analysis_complete),
        ("multi_event_design", multi_event_design),
        ("environmental_effect_closure", evidence.effect_closure_ready),
        ("event_snr_report_complete", event_snrs_complete),
        ("positive_ocean_coefficient_ci", coefficient_positive),
        ("all_heldout_events_improve", heldout_improvement_passes),
        ("heldout_quiet_far", evidence.heldout_quiet_far_passes is True),
        ("sensitivity_analysis", evidence.sensitivity_analysis_complete),
        ("failed_event_log", evidence.failed_event_log_complete),
    )
    required_success = dict(gates)
    full_claim_ready = all(required_success.values()) and novelty_count >= 3

    blocking = tuple(name for name, passes in gates if not passes)
    if full_claim_ready:
        branch = "successful_attribution"
    elif not (
        evidence.uses_real_observations
        and evidence.data_gate_passes
        and evidence.analysis_complete
    ):
        branch = "pending_evidence"
    elif evidence.typhoon_event_count < 3 and coefficient_positive:
        branch = "single_case_short_paper"
    elif not (
        multi_event_design
        and evidence.effect_closure_ready
        and evidence.direct_deformation_separated
        and evidence.multi_source_validation_complete
        and evidence.sensitivity_analysis_complete
        and evidence.failed_event_log_complete
        and event_snrs_complete
        and evidence.heldout_quiet_far_passes is not None
        and heldout_results_complete
    ):
        branch = "pending_evidence"
    elif (
        not coefficient_positive
        and not any(evidence.heldout_improvement_passes)
        and max(evidence.event_snrs) < evidence.minimum_interpretable_event_snr
    ):
        branch = "non_detection_constraints"
    else:
        branch = "ocean_product_evaluation"

    return Paper2DecisionAudit(
        branch=branch,
        full_attribution_claim_ready=full_claim_ready,
        manuscript_release_ready=(
            full_claim_ready and evidence.data_license_review_complete
        ),
        novelty_requirement_count=novelty_count,
        novelty_requirements=novelty,
        gates=gates,
        blocking_reasons=blocking,
        event_snr_count=len(evidence.event_snrs),
        event_snr_minimum=min(evidence.event_snrs) if evidence.event_snrs else None,
        event_snr_maximum=max(evidence.event_snrs) if evidence.event_snrs else None,
    )
