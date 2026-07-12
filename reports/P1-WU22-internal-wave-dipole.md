# P1-WU22 compensated internal-wave density dipole

Status: compensated 3-D direct-attraction primitive implemented; stratified-fluid priors and free-surface coupling pending

## Source model

Two anisotropic three-dimensional Gaussian density lobes have identical horizontal/vertical scales and opposite signs. Their centres are separated vertically. The discretized weights are exact sign copies, so net signed mass is zero before and after multiplication by the periodic peak-density anomaly.

The complete unit-density volume-cell response is calculated once, then scaled by `rho'_peak cos(2 pi t/P + phase)`. This preserves linearity while avoiding repeated three-dimensional integration.

## Predefined acceptance checks

- Positive and negative discrete lobe masses cancel within relative `1e-15`.
- Two full cycles repeat, have negligible gravity mean, and peak spectrally at `1/P`.
- Peak density magnitude scales gravity linearly and changing its sign reverses the signal.
- A phase shift of pi reverses the complete response.
- Invalid period, scales, separation, grid, and coordinates are rejected.

## Scope

This is a controlled compensated-density primitive, not a solved internal-wave eigenmode. It omits realistic stratification, modal vertical structure, interface displacement-to-density conversion, a dynamically consistent free-surface response, bathymetry, propagation, and elastic Earth loading. Its purpose is to enforce mass cancellation and quantify why same-volume surface-water estimates overstate internal-wave gravity.

