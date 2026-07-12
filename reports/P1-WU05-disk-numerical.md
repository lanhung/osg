# P1-WU05 numerical disk integration validation

Status: implemented; awaiting independent human review  
Method: composite midpoint integration in polar coordinates  
Units/frame: SI; local Cartesian, `z` positive upward

## Design

The reference implementation integrates point-cell attraction over radius and azimuth. Polar-cell area is `r dr dtheta`; midpoint radii preserve the exact total disk area for every positive radial resolution. This implementation is intentionally transparent and dependency-free. It is a validation reference, not yet the optimized production gridded-load engine.

## Predefined acceptance checks

- On-axis vertical acceleration agrees with the independent analytic disk solution within `1e-4` relative error at the frozen grid.
- Off-axis reflection reverses the horizontal component and preserves the vertical component.
- Joint translation of source and observer preserves the vector.
- Negative density anomaly reverses all vector components.
- At `100 R`, the numerical disk agrees with the equal-mass point source within 1%.
- Consecutive radial refinement reduces analytic error, with the 32-cell error below one tenth of the 8-cell error.
- An observation inside the ideal disk plane and invalid grid sizes are rejected.

## Result

All checks pass. Production integration still requires spherical geometry, coastline/missing-cell rules, chunking, deterministic summation, and performance benchmarks.

