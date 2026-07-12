# P1-WU04 finite thin-disk validation

Status: implemented; awaiting independent human review  
Units: SI  
Frame: horizontal disk in local Cartesian coordinates, `z` positive upward

## Model

For a uniform disk of radius `R`, signed surface density `sigma`, and positive axial separation magnitude `h`, the one-sided axial magnitude is

```text
2 pi G sigma [1 - h / sqrt(h^2 + R^2)].
```

The implementation uses the algebraically equivalent expression

```text
R^2 / {sqrt(h^2 + R^2) [sqrt(h^2 + R^2) + h]}
```

for the bracketed geometry factor. This avoids catastrophic cancellation in the point-mass far field.

## Predefined acceptance checks

- Direct analytic expression agreement at an intermediate radius/separation ratio.
- Attraction points toward a positive disk on either side.
- Negative surface-density anomaly reverses the field.
- At axial separation `100 R`, the equal-mass point-source relative error is below 1%.
- As `R/h` becomes very large, the result approaches the one-sided infinite-sheet limit `2 pi G sigma`.
- Zero density returns zero.
- In-plane observation and non-positive radius are rejected.

## Result

All checks pass. The zero-thickness disk field is discontinuous at its plane; this API deliberately rejects an exactly in-plane observation rather than hiding the ambiguity. Off-axis numerical integration remains a separate work unit.

