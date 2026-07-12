"""Metadata-level environmental-effect ownership and ambiguity gate."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EffectDeclaration:
    source_id: str
    effect_id: str
    status: str
    evidence: str

    def __post_init__(self) -> None:
        if not self.source_id.strip() or not self.effect_id.strip() or not self.evidence.strip():
            raise ValueError("effect source, effect ID, and evidence must be non-empty")
        if self.status not in {"included", "excluded", "unknown"}:
            raise ValueError("effect declaration status must be included, excluded, or unknown")


@dataclass(frozen=True, slots=True)
class EffectOwnershipResult:
    effect_id: str
    status: str
    included_sources: tuple[str, ...]
    unknown_sources: tuple[str, ...]
    excluded_sources: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class EffectLedgerAudit:
    closure_ready: bool
    effects: tuple[EffectOwnershipResult, ...]


def audit_effect_ledger(
    declarations: Sequence[EffectDeclaration],
    *,
    required_effect_ids: Sequence[str],
) -> EffectLedgerAudit:
    """Require one unambiguous owner for every required physical effect."""

    rows = tuple(declarations)
    if not rows:
        raise ValueError("effect ledger must contain declarations")
    required = tuple(sorted(set(required_effect_ids)))
    if not required or any(not effect.strip() for effect in required):
        raise ValueError("required effect IDs must be non-empty")
    declared_effects = {row.effect_id for row in rows}
    undeclared = set(required) - declared_effects
    all_effects = tuple(sorted(declared_effects | set(required)))
    results = []
    for effect in all_effects:
        relevant = tuple(row for row in rows if row.effect_id == effect)
        included = tuple(sorted(row.source_id for row in relevant if row.status == "included"))
        unknown = tuple(sorted(row.source_id for row in relevant if row.status == "unknown"))
        excluded = tuple(sorted(row.source_id for row in relevant if row.status == "excluded"))
        if effect in undeclared or len(included) == 0:
            status = "missing_owner"
        elif len(included) > 1:
            status = "duplicate_owner"
        elif unknown:
            status = "ambiguous_possible_overlap"
        else:
            status = "closed"
        results.append(EffectOwnershipResult(effect, status, included, unknown, excluded))
    return EffectLedgerAudit(
        closure_ready=all(
            result.status == "closed" for result in results if result.effect_id in required
        ),
        effects=tuple(results),
    )
