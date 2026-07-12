# P2-WU05 SG time-series quality summary

Status: implemented and unit-tested

## Output

Given declared cadence and a unit-explicit discontinuity threshold, the summary
reports missing fraction, missing count, cadence breaks, retained uniform
segments, dropped short runs, candidate discontinuity indices, and maximum
finite adjacent difference.

Indices refer to the original input record even across gaps and cadence breaks.
The threshold is supplied by the caller; the module does not infer an instrument
threshold from the event being studied.

## Safety boundary

Flags are not classified automatically as spikes, earthquakes, maintenance,
instrument steps, or real environmental signals. No sample is deleted, replaced,
interpolated, step-corrected, or detrended. Those actions require instrument logs,
predeclared rules, saved correction series and sensitivity analysis.

This provides the first Gate 2 primitive but does not constitute a station data
quality report until real gravity, pressure, timing and status records are loaded.
