# P1-WU45 compensated three-dimensional density eddy

Status: implemented and physics-tested

## Model

A positive anisotropic Gaussian density core is surrounded by a broader negative
Gaussian halo at the same depth. The halo amplitude is solved from the actual
discretized weights and cell volumes, so signed mass cancels to floating
tolerance before the user density amplitude is applied. The balanced structure
translates at constant horizontal speed.

The result exposes local core-density amplitude, direct vertical gravity, `Tzz`,
positive/negative unit-density masses, halo scaling and grid size.

## Acceptance checks

- Discrete core and halo mass cancel to relative `2e-15`.
- Central passage is symmetric in gravity and gradient.
- Density sign reversal reverses both observables exactly.
- At 500 km height the compensated gravity peak is below `1e-3` of the 20 km
  result for the validation geometry.
- Invalid halo scale and zero translation speed fail.

## Scientific use

This supplies the required compensation variant alongside the SSH-only eddy.
Its Gaussian profile and parameters remain engineering fixtures. Chelton et al.
(2011) profile/radius definitions and catalogue distributions must be audited
before the model enters a scientific scenario ensemble.
