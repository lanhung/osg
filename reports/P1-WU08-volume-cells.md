# P1-WU08 three-dimensional density-cell integration

Status: implemented; awaiting independent human review  
Discretization: constant-density cells represented by centre point masses  
Summation: deterministic `math.fsum` per vector component

## Contract

Inputs are signed SI density anomalies, cell centres, positive cell volumes, and one observation coordinate. The method is a reference discretization: every scientific use must demonstrate spatial convergence. A nonzero point-cell located exactly at the observation point is rejected because replacing the containing volume by a singular point mass is invalid.

## Predefined acceptance checks

- One volume cell agrees with a point mass of `density * volume` within relative `2e-15` floating-point tolerance.
- Symmetric cell pairs cancel horizontal acceleration.
- Equal and opposite colocated density anomalies cancel.
- Translating all cells and the observer together preserves gravity.
- A `20^3` three-dimensional Gaussian grid observed at `20` scale lengths agrees with the exact total-mass point source within 1%.
- Zero-density cells at the observer are harmless; nonzero singular cells are rejected.
- Array lengths, volumes, coordinates, and finite values are validated.

## Result

All checks pass. This establishes the general three-dimensional density-anomaly primitive. Process-specific convergence and compensation tests for mesoscale eddies, internal waves, and landslides remain required.
