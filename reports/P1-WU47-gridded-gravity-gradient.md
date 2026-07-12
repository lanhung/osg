# P1-WU47 spherical and WGS 84 gridded gravity gradients

Status: full ECEF tensor and local vertical projection implemented

## Convention

Each nonzero surface-cell mass contributes the established point tensor
`T_ij = ∂g_i/∂x_observation_j`. Spherical grids return the ECEF tensor and
radial–radial projection; WGS 84 grids return the ECEF tensor and
geodetic-up–up projection. The time-varying gridded SSH adapter now propagates
that local vertical gradient as `Tzz`.

## Acceptance checks

- Spherical radial gradient agrees with a central difference in observation
  height to relative `2e-7`.
- WGS 84 geodetic-up gradient meets the same independent check.
- ECEF tensors are symmetric and trace-free outside source cells.
- Zero/positive/negative gridded SSH scales `Tzz` linearly with mass.
- Existing registered experiment checksums remain unchanged.

## Scope

This is direct attraction only. Instrument axes may differ from local vertical,
and elastic-load gradients are not supplied by the current provider contract.
Those transformations must be explicit before comparison with a real
gradiometer.
