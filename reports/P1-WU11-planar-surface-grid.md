# P1-WU11 local planar surface-load grid

Status: implemented; awaiting independent human review  
Axes: rows increase in local `y`, columns increase in local `x`  
Cell model: signed surface density times exact planar cell area, located at area centroid

## Data and accounting contract

- Sea-level anomaly converts to surface density as `rho_water * eta`; wave significant height is not accepted as mean load.
- Edge arrays may be irregular but must be finite and strictly increasing.
- `water_mask=False` represents excluded land/non-water cells.
- Missing cells are `None` or non-finite values and must either raise or be explicitly counted under `missing_policy='skip'`.
- The result includes gravity, included area/mass/cell count, masked count, and missing count.
- Vector components and mass are accumulated with deterministic `math.fsum`.

## Predefined acceptance checks

- One grid cell equals a centroid point mass and preserves exact area/mass.
- A symmetric 2x2 load cancels horizontal acceleration.
- Irregular-area mask/missing accounting closes exactly.
- Refining a uniform grid over a finite rectangle converges monotonically to the independent analytic solution; the frozen finest grid is below 1% relative error and below one tenth of the coarsest absolute error.
- Ragged grids, non-increasing edges, silent missing data, and a singular observation-centroid geometry are rejected.

## Result

All checks pass. This is a local planar direct-attraction reference. Spherical geometry, longitude wrap, ellipsoidal cell area, coastline-resolution sensitivity, domain truncation, and optimized chunking remain separate gates.

