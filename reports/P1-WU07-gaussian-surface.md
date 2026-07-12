# P1-WU07 Gaussian surface-anomaly validation

Status: implemented; awaiting independent human review  
Profile: `sigma(r) = sigma0 exp[-r^2/(2 L^2)]`  
Total signed mass: `2 pi sigma0 L^2`

## Analytic benchmark

The axial field is evaluated from the closed form

```text
2 pi G sigma0 {1 - sqrt(pi/2) q exp(q^2/2) erfc[q/sqrt(2)]},
q = h/L.
```

For `q >= 12`, a far-field asymptotic expansion is used to avoid overflow and subtraction of nearly equal numbers. The numerical reference integrates polar midpoint cells to `8 L`; the exact omitted mass fraction is `exp(-32)`, below `1e-13`.

## Predefined acceptance checks

- Frozen numerical grid agrees with the analytic axis field within `5e-4` relative error.
- At `h = 100 L`, the analytic Gaussian agrees with its exact-total-mass point source within 1%.
- Large `L/h` approaches the one-sided infinite-sheet field.
- Sign, side-of-plane direction, refinement, and input validation behave physically.

## Result

All checks pass. This model is a surface-mass anomaly; a compensated three-dimensional eddy or internal-wave density structure requires the separate volume/dipole work unit and must not reuse this signal magnitude uncritically.

