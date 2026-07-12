"""Claim-safe evaluation of scalar published-case reproduction targets."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CaseTarget:
    target_id: str
    expected_value: float
    unit: str
    tolerance_kind: str
    tolerance: float
    source: str

    def __post_init__(self) -> None:
        if not self.target_id.strip() or not self.unit.strip() or not self.source.strip():
            raise ValueError("target ID, unit, and source must be non-empty")
        if not math.isfinite(self.expected_value):
            raise ValueError("expected_value must be finite")
        if self.tolerance_kind not in {"absolute", "fractional"}:
            raise ValueError("tolerance_kind must be absolute or fractional")
        if not math.isfinite(self.tolerance) or self.tolerance < 0.0:
            raise ValueError("tolerance must be finite and nonnegative")
        if self.tolerance_kind == "fractional" and self.expected_value == 0.0:
            raise ValueError("fractional tolerance is undefined for a zero target")


@dataclass(frozen=True, slots=True)
class CaseTargetResult:
    target_id: str
    status: str
    expected_value: float
    observed_value: float | None
    error: float | None
    tolerance: float
    tolerance_kind: str
    unit: str


@dataclass(frozen=True, slots=True)
class CaseReproductionAudit:
    case_id: str
    status: str
    targets: tuple[CaseTargetResult, ...]


def evaluate_case_reproduction(
    case_id: str,
    targets: Sequence[CaseTarget],
    observed_values: Mapping[str, float],
) -> CaseReproductionAudit:
    """Evaluate only declared observations; absent targets remain pending."""

    if not case_id.strip():
        raise ValueError("case_id must be non-empty")
    rows = tuple(targets)
    if not rows:
        raise ValueError("at least one case target is required")
    identifiers = [target.target_id for target in rows]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("case target IDs must be unique")
    unknown = set(observed_values) - set(identifiers)
    if unknown:
        raise ValueError(f"observations contain undeclared targets: {sorted(unknown)}")

    results = []
    for target in rows:
        raw_observed = observed_values.get(target.target_id)
        if raw_observed is None:
            results.append(
                CaseTargetResult(
                    target_id=target.target_id,
                    status="pending",
                    expected_value=target.expected_value,
                    observed_value=None,
                    error=None,
                    tolerance=target.tolerance,
                    tolerance_kind=target.tolerance_kind,
                    unit=target.unit,
                )
            )
            continue
        observed = float(raw_observed)
        if not math.isfinite(observed):
            raise ValueError(f"observed value for {target.target_id!r} must be finite")
        absolute_error = abs(observed - target.expected_value)
        error = (
            absolute_error
            if target.tolerance_kind == "absolute"
            else absolute_error / abs(target.expected_value)
        )
        results.append(
            CaseTargetResult(
                target_id=target.target_id,
                status="pass" if error <= target.tolerance else "fail",
                expected_value=target.expected_value,
                observed_value=observed,
                error=error,
                tolerance=target.tolerance,
                tolerance_kind=target.tolerance_kind,
                unit=target.unit,
            )
        )
    statuses = {result.status for result in results}
    overall = "fail" if "fail" in statuses else "pending" if "pending" in statuses else "pass"
    return CaseReproductionAudit(case_id=case_id, status=overall, targets=tuple(results))
