# P3-WU06 reliable magnitude time

Status: implemented and unit-tested

## Metrics

For each decision time and held-out event set, the evaluator reports magnitude
MAE, signed bias, sensitivity for the predeclared high-risk class (default
`Mw >= 8.2`), specificity for the lower-risk class, and optional prediction-
interval coverage.

Reliable magnitude time is the first sustained point satisfying every declared
criterion. If the held-out set lacks either risk class, reliability cannot be
claimed because sensitivity or specificity is undefined. Missing interval
coverage likewise fails when coverage was required.

## Consequence

PEGS detection time and reliable-Mw time are now separate quantities. Paper 3
must freeze acceptable MAE, risk-class performance, interval coverage and
persistence before test evaluation, then compare the resulting reliable-Mw time
with W-phase/GNSS/conventional estimates using the warning timeline contract.
