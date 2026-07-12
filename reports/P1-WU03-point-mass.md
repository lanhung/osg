# P1-WU03 point-mass validation

Status: implemented; awaiting independent human review  
Units: SI  
Frame: local Cartesian `(x, y, z)`, `z` positive upward

## Model

For signed source mass `m`, source position `x_s`, and observation position `x_o`,

```text
g(x_o) = G m (x_s - x_o) / |x_s - x_o|^3.
```

A positive mass attracts the observer toward the source. A negative density/mass anomaly reverses the vector. Coincident source and observation coordinates are rejected because the point-source idealization is singular there.

## Predefined acceptance checks

- Axis-aligned vector agrees with `G m / r^2` to floating-point precision.
- General three-dimensional vector magnitude agrees with `G m / r^2`.
- Doubling distance reduces acceleration magnitude by four.
- Translating source and observer together does not change acceleration.
- Negative mass exactly reverses direction.
- Zero mass away from the source returns the zero vector.
- Coincident or non-finite geometry is rejected rather than emitting NaN/Inf.

## Result

All checks pass using the dependency-free standard-library suite. This work unit validates only the point-source primitive; it makes no detectability or ocean-process claim.

