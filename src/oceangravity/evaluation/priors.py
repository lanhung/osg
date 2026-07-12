"""Evidence-aware parameter envelopes and deterministic design sampling."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from .sampling import ParameterRange, latin_hypercube


@dataclass(frozen=True, slots=True)
class ParameterEnvelope:
    """A bounded design dimension with explicit evidence and semantics."""

    name: str
    unit: str
    lower: float
    upper: float
    scale: str
    evidence_status: str
    range_semantics: str
    sources: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.unit.strip():
            raise ValueError("parameter unit must not be empty")
        ParameterRange(self.name, self.lower, self.upper, self.scale)
        if self.evidence_status not in {
            "engineering_fixture",
            "literature_supported",
            "data_derived",
        }:
            raise ValueError("unsupported evidence_status")
        if self.range_semantics not in {"scenario_envelope", "probability_prior"}:
            raise ValueError("unsupported range_semantics")
        if self.evidence_status in {"literature_supported", "data_derived"} and not self.sources:
            raise ValueError("literature/data-supported envelopes require sources")
        if (
            self.range_semantics == "probability_prior"
            and self.evidence_status == "engineering_fixture"
        ):
            raise ValueError("an engineering fixture cannot be labelled a probability prior")
        if any(not source.strip() for source in self.sources):
            raise ValueError("envelope sources must be non-empty strings")

    def as_parameter_range(self) -> ParameterRange:
        return ParameterRange(self.name, self.lower, self.upper, self.scale)


@dataclass(frozen=True, slots=True)
class ParameterDesign:
    """Sampled design plus the interpretation callers must propagate."""

    samples: tuple[dict[str, float], ...]
    interpretation: str
    evidence_statuses: tuple[str, ...]


def sample_parameter_design(
    envelopes: Sequence[ParameterEnvelope],
    sample_count: int,
    *,
    random_seed: int,
) -> ParameterDesign:
    """Latin-hypercube sample without promoting scenarios to probabilities."""

    if not envelopes:
        raise ValueError("at least one parameter envelope is required")
    samples = latin_hypercube(
        [envelope.as_parameter_range() for envelope in envelopes],
        sample_count,
        random_seed=random_seed,
    )
    all_probability = all(envelope.range_semantics == "probability_prior" for envelope in envelopes)
    interpretation = (
        "probability_prior_samples"
        if all_probability
        else "space_filling_scenario_design_not_probability_samples"
    )
    return ParameterDesign(
        samples=samples,
        interpretation=interpretation,
        evidence_statuses=tuple(sorted({item.evidence_status for item in envelopes})),
    )
