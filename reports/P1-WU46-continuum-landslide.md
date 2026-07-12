# P1-WU46 continuum Gaussian submarine landslide

Status: implemented and physics-tested

## Model

The slide relocates identical anisotropic Gaussian solid volumes from source to
destination. Discrete density is normalized to the requested solid mass; source
and destination arrays are exact sign copies. A half-cosine transition retains
the point-pair model's smooth start/end while gravity and `Tzz` use the full
volume-cell field.

## Acceptance checks

- Signed discrete mass closes to relative `2e-15`.
- Pre-slide, midpoint, completed and post-slide fractions are exact.
- A narrow Gaussian at 100 km approaches the independent point-pair gravity
  within relative `2e-6`.
- Joint source/destination/observer translation preserves gravity.
- Invalid scales and grids fail.

## Remaining physics

The continuum solid model removes the point-mass singular idealization, but it
does not model deformation of the slide body, acceleration history beyond the
scalar ramp, water entrainment, bathymetry, or the generated tsunami. Those
parameters require cited landslide scenarios and coupled hydrodynamics before
paper-level use.
