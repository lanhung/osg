# P1-WU06 finite rectangular surface-load validation

Status: implemented; awaiting independent human review  
Methods: analytic centre-axis solution and Cartesian midpoint integration  
Units/frame: SI; local Cartesian, `z` positive upward

## Analytic benchmark

For half widths `a` and `b` and perpendicular separation `h`, the centred axial field magnitude is

```text
4 G sigma atan[ab / (h sqrt(h^2 + a^2 + b^2))].
```

The implementation uses `atan2` for stable limiting behaviour. The numerical reference divides the exact rectangle area into equal midpoint cells.

## Predefined acceptance checks

- Numerical axial field agrees with the analytic solution within `1e-4` relative error at the frozen grid.
- Exchanging half widths leaves the analytic result unchanged.
- A positive load attracts from either side; a very large rectangle approaches `2 pi G sigma`.
- At a distance 100 times the largest half width, the rectangle agrees with an equal-mass point source within 1%.
- Grid refinement monotonically reduces error, with the finest error below one tenth of the coarsest.
- Off-axis reflection reverses the corresponding horizontal component and preserves vertical gravity.
- Invalid dimensions, grid counts, and in-load-plane observations are rejected.

## Result

All checks pass. This work unit supplies a finite-cell benchmark for later regular-grid ocean loading; spherical-cell geometry and coastline/missing-cell conventions remain separate gates.

