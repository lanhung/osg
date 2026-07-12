# P1-WU41 gridded-load convergence gates

Status: mass closure, refinement, truncation, sign and component-sum evidence complete

## Acceptance checks

- A signed equal-area spherical load closes total mass to the declared floating
  tolerance.
- For a localized Gaussian load on a fixed 4° domain, refining 16² → 32² → 64²
  cells reduces error, and the 32² response is within 2% of the 64² reference.
- At approximately fixed 0.125° resolution, expanding half-width 2° → 4° → 6°
  reduces domain-truncation error, and the 4° result is within 1% of the 6°
  reference.
- Earlier physics tests already cover signed density/load reversal, masks,
  missing values, longitude wrap, spherical shell behavior, planar/spherical and
  WGS 84 comparisons.
- The Green-function contract test verifies total gravity is exactly the sum of
  direct attraction, deformation gravity, and internal-mass gravity; vertical
  displacement cannot leak into that sum.

## Scope

The Gaussian tests are numerical convergence fixtures, not ocean-process
priors. Production datasets still require their own resolution and domain
sensitivity using actual coastlines, missing masks, and elastic kernels.
