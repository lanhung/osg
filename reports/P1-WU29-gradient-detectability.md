# P1-WU29 gravity-gradient detectability interface

Status: implemented and unit-tested

## Scope

The coverage-aware detectability evaluator now supports gravity-gradient time
series through a dedicated public wrapper. The numerical SNR and spectral
coverage implementation is shared with vertical gravity, while observable and
ASD-unit checks remain explicit at the API boundary.

## Acceptance checks

- A gradient signal is accepted only with `observable=gravity_gradient` and
  `asd_unit=s^-2 Hz^-1/2`.
- Passing the same gradient curve to the vertical-gravity wrapper raises an
  error instead of silently mixing observables.
- The existing vertical-gravity behavior remains unchanged.
- The complete unit, physics, regression, and workflow suite passes.

## Result

All 176 tests pass. This interface is the bounded prerequisite for registering
`P1-E003`, which will compare the six process `Tzz` series only against the two
traceable gradient-instrument anchors.
