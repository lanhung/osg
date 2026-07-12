# P1-WU40 WGS 84 surface-load geometry

Status: reference ellipsoidal integrator implemented and physics-tested

## Method

The WGS 84 adapter uses defining semi-major axis 6,378,137 m and inverse
flattening 298.257223563. It integrates the oblate-ellipsoid surface element
exactly for cell area, bisects that area coordinate for latitude centroids, and
uses geodetic ECEF coordinates for source and observer. Gravity is returned in
ECEF and projected onto local geodetic up.

Source/load height is explicit. This permits controlled topography/sea-surface
height sensitivity without silently changing the cell-area reference surface.

## Acceptance checks

- A global grid closes to the analytic WGS 84 oblate-spheroid surface area at
  relative `3e-15`.
- A 4° × 4° regional patch around 20°N agrees with the mean-radius spherical
  implementation within 1%, while retaining a measurable nonzero difference.
- A 1 km source-height change modifies attraction as expected.
- Mask, missing-value and invalid-geometry accounting remains explicit.

## Limitation

Cells are still represented by point masses at area centroids. Geoid–ellipsoid
separation, bathymetry, coastal partial cells, and within-cell quadrature require
separate sensitivity tests for production ocean grids.
