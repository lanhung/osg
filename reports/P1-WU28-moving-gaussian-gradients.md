# P1-WU28 moving Gaussian surface gravity gradients

Status: implemented; all six process primitives now expose direct vertical gravity and `Tzz`

## Method

The Gaussian surface integrator now accumulates gravity vector and vertical gradient in one polar-cell pass. For each point-cell mass `m` and displacement `d`,

```text
Tzz_cell = G m (3 d_z^2/r^5 - 1/r^3).
```

The translating SSH eddy records this response at every centre position. The tsunami packet sums crest and equal/opposite trough gradients separately with deterministic `fsum`.

## Predefined acceptance checks

- On-axis numerical Gaussian `Tzz` agrees with a finite difference of the independent analytic Gaussian gravity within relative `5e-4`.
- Off-axis `Tzz` agrees with finite differences of the numerical gravity under an identical grid within relative `2e-8`.
- At 100 Gaussian scales, `Tzz` agrees with the exact-total-mass point tensor within 1%.
- Signed surface density reverses gradient.
- Every one of the six foundation process signals has a finite nonzero vertical-gradient series.
- Existing registered gravity-only output SHA-256 values remain unchanged.

## Result

All checks pass. Gradient detectability remains separate because only two gradient-instrument anchors exist and process parameters are still engineering fixtures. The next experiment must compare gradient signal spectra only with `gravity_gradient` ASD curves and apply the same frequency-coverage gate.

