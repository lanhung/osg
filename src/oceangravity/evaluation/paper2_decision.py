"""Claim-safe Paper 2 manuscript-branch decision audit."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Paper2DecisionEvidence:
    uses_real_observations: bool
    analysis_complete: bool
    data_gate_passes: bool
    typhoon_event_count: int
    heldout_event_count: int
    quiet_window_count: int
    effect_closure_ready: bool
    direct_deformation_separated: bool
    multi_source_validation_complete: bool
    sensitivity_analysis_complete: bool
    failed_event_log_complete: bool
    data_license_review_complete: bool
    attribution_ci_lower_bound: float | None
    heldout_improvement_passes: tuple[bool, ...]
    heldout_quiet_far_passes: bool | None
    event_snrs: tuple[float, ...]
    event_snr_interpretation_threshold: float

    def __post_init__(self) -> None:
        flags = (
            self.uses_real_observations,
            self.analysis_complete,
            self.data_gate_passes,
            self.effect_closure_ready,
            self.direct_deformation_separated,
            self.multi_source_validation_complete,
            self.sensitivity_analysis_complete,
            self.failed_event_log_complete,
            self.data_license_review_complete,
        )
        if any(not isinstance(value, bool) for value in flags):
            raise ValueError("Paper 2 decision flags must be boolean")
        counts = (
            self.typhoon_event_count,
            self.heldout_event_count,
            self.quiet_window_count,
        )
        if any(
            isinstance(value, bool) or not isinstance(value, int) or value < 0
            for value in counts
        ):
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
        if self.attribution_ci_lower_bound is not None and not math.isfinite(
            self.attribution_ci_lower_bound
        ):
            raise ValueError("attribution CI lower bound must be finite or None")
        if len(self.event_snrs) > self.typhoon_event_count:
            raise ValueError("event SNR results exceed declared typhoon events")
        if not all(math.isfinite(value) and value >= 0.0 for value in self.event_snrs):
            raise ValueError("event SNR values must be finite and non-negative")
        threshold = self.event_snr_interpretation_threshold
        if not math.isfinite(threshold) or threshold <= 0.0:
            raise ValueError("event SNR interpretation threshold must be finite and positive")


@dataclass(frozen=True, slots=True)
class Paper2NoveltyAudit:
    event_resolved_attribution: bool
    direct_gravity_deformation_separation: bool
    multi_source_closed_loop_validation: bool
    cross_typhoon_generalization: bool
    demonstrated_count: int
    minimum_required_count: int
    passes: bool


@dataclass(frozen=True, slots=True)
class Paper2DecisionAudit:
    branch: str
    full_attribution_claim_ready: bool
    manuscript_release_ready: bool
    novelty: Paper2NoveltyAudit
    positive_attribution_interval: bool
    heldout_evaluation_complete: bool
    all_heldout_events_improve: bool
    event_snr_reporting_complete: bool
    events_above_snr_interpretation_threshold: int
    blocking_reasons: tuple[str, ...]


def audit_paper2_decision(evidence: Paper2DecisionEvidence) -> Paper2DecisionAudit:
    """Select a preregistered branch without turning missing evidence into failure."""

    positive_interval = (
        evidence.attribution_ci_lower_bound is not None
        and evidence.attribution_ci_lower_bound > 0.0
    )
    heldout_complete = (
        evidence.heldout_event_count > 0
        and len(evidence.heldout_improvement_passes) == evidence.heldout_event_count
    )
    all_heldout_improve = heldout_complete and all(
        evidence.heldout_improvement_passes
    )
    multi_event_design = (
        evidence.typhoon_event_count >= 3
        and evidence.heldout_event_count >= 1
        and evidence.quiet_window_count >= 3
    )
    snr_complete = (
        evidence.typhoon_event_count > 0
        and len(evidence.event_snrs) == evidence.typhoon_event_count
    )
    events_above_snr = sum(
        value >= evidence.event_snr_interpretation_threshold
        for value in evidence.event_snrs
    )

    real = evidence.uses_real_observations
    novelty_values = (
        real and positive_interval,
        real and evidence.effect_closure_ready and evidence.direct_deformation_separated,
        real and evidence.multi_source_validation_complete,
        real and multi_event_design and all_heldout_improve,
    )
    novelty_count = sum(novelty_values)
    novelty = Paper2NoveltyAudit(
        event_resolved_attribution=novelty_values[0],
        direct_gravity_deformation_separation=novelty_values[1],
        multi_source_closed_loop_validation=novelty_values[2],
        cross_typhoon_generalization=novelty_values[3],
        demonstrated_count=novelty_count,
        minimum_required_count=3,
        passes=novelty_count >= 3,
    )

    scientific_gates = (
        real,
        evidence.analysis_complete,
        evidence.data_gate_passes,
        multi_event_design,
        evidence.effect_closure_ready,
        evidence.direct_deformation_separated,
        evidence.multi_source_validation_complete,
        evidence.sensitivity_analysis_complete,
        evidence.failed_event_log_complete,
        positive_interval,
        all_heldout_improve,
        evidence.heldout_quiet_far_passes is True,
        snr_complete,
        novelty.passes,
    )
    full_claim_ready = all(scientific_gates)

    reason_flags = (
        ("real_observations_missing", not real),
        ("analysis_not_complete", not evidence.analysis_complete),
        ("data_gate_not_passed", not evidence.data_gate_passes),
        ("multi_event_design_incomplete", not multi_event_design),
        ("effect_ownership_not_closed", not evidence.effect_closure_ready),
        ("direct_deformation_separation_incomplete", not evidence.direct_deformation_separated),
        ("multi_source_validation_incomplete", not evidence.multi_source_validation_complete),
        ("sensitivity_analysis_incomplete", not evidence.sensitivity_analysis_complete),
        ("failed_event_log_incomplete", not evidence.failed_event_log_complete),
        ("attribution_interval_not_positive", not positive_interval),
        ("heldout_improvement_not_demonstrated", not all_heldout_improve),
        ("quiet_false_alarm_gate_not_passed", evidence.heldout_quiet_far_passes is not True),
        ("event_snr_reporting_incomplete", not snr_complete),
        ("fewer_than_three_novelty_requirements", not novelty.passes),
        ("data_license_review_incomplete", not evidence.data_license_review_complete),
    )
    blocking = tuple(name for name, active in reason_flags if active)

    single_case_ready = (
        1 <= evidence.typhoon_event_count < 3
        and positive_interval
        and evidence.effect_closure_ready
        and evidence.direct_deformation_separated
        and evidence.multi_source_validation_complete
        and evidence.sensitivity_analysis_complete
        and evidence.failed_event_log_complete
        and evidence.heldout_quiet_far_passes is True
        and snr_complete
    )
    if full_claim_ready:
        branch = "successful_attribution"
    elif not (real and evidence.analysis_complete and evidence.data_gate_passes):
        branch = "pending_evidence"
    elif single_case_ready:
        branch = "single_case_short_paper"
    elif not (
        multi_event_design
        and evidence.effect_closure_ready
        and evidence.direct_deformation_separated
        and evidence.multi_source_validation_complete
        and evidence.sensitivity_analysis_complete
        and evidence.failed_event_log_complete
        and heldout_complete
        and evidence.heldout_quiet_far_passes is not None
        and snr_complete
    ):
        branch = "pending_evidence"
    elif not positive_interval and not any(evidence.heldout_improvement_passes) and events_above_snr == 0:
        branch = "non_detection_constraints"
    else:
        branch = "ocean_product_evaluation"

    return Paper2DecisionAudit(
        branch=branch,
        full_attribution_claim_ready=full_claim_ready,
        manuscript_release_ready=(
            full_claim_ready and evidence.data_license_review_complete
        ),
        novelty=novelty,
        positive_attribution_interval=positive_interval,
        heldout_evaluation_complete=heldout_complete,
        all_heldout_events_improve=all_heldout_improve,
        event_snr_reporting_complete=snr_complete,
        events_above_snr_interpretation_threshold=events_above_snr,
        blocking_reasons=blocking,
    )
