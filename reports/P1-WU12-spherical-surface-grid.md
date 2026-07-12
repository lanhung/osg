# P1-WU12 spherical surface-load grid

Status: implemented; awaiting independent human review  
Earth model: sphere with IUGG mean radius `6,371,008.8 m`  
Output: ECEF gravity vector and local outward-positive radial component

## Geometry contract

- Latitude rows are strictly increasing within `[-90, 90]` degrees.
- Longitude edges are strictly increasing in an unwrapped coordinate and may cross the antimeridian, for example `[170, 180, 190]`.
- Exact spherical cell area is `R^2 delta_lon (sin(lat_north)-sin(lat_south))`.
- The point-cell source uses midpoint longitude and midpoint `sin(latitude)`, the equal-area coordinate.
- The model is a spherical reference, not an ellipsoidal or topographic near-field solution.

## Predefined acceptance checks

- A global grid sums to `4 pi R^2` within floating-point tolerance.
- A uniformly loaded global spherical shell observed at radius `2R` agrees with a central point mass within 1% (discretized shell-theorem check).
- Equivalent antimeridian grids in `[170,190]` and `[-190,-170]` are invariant.
- A small equatorial patch agrees with the local planar model within 1%.
- Missing, mask, latitude, longitude-span, and shape rules remain explicit.

## Result

All checks pass. Remaining production work includes ellipsoidal/topographic sensitivity, exact or refined treatment of the station-containing coastal cell, chunked array execution, and domain-truncation tests.

