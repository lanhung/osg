# P3-WU05 time-dependent held-out detection

Status: implemented and unit-tested

## Contract

A threshold frozen on noise-only calibration is evaluated across completely
held-out signal events at every declared time after origin. Each point stores
detected count, total event count and empirical detection probability.

The earliest reliable time is the first point meeting the predeclared detection
probability. Callers may require multiple consecutive qualifying time points so
that a transient score crossing is not reported as a stable warning decision.
If no crossing occurs, the result is `None`, not the final evaluation time.

## Paper 3 use

The main experiment will combine this function with the empirical false-alarm
threshold from `P3-WU04`, reporting detection probability versus time separately
by magnitude, rupture segment, noise stratum, network variant and station-outage
condition. A 90% target and persistence rule must be frozen before examining
test results.
