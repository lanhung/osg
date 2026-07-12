# P1-WU42 partial coastal-cell loading

Status: implemented consistently for planar, spherical, and WGS 84 grids

## Convention

`cell_load_fraction` is a dimensionless 0–1 fraction of each geometric cell
occupied by the represented load. Effective area, mass, and point-cell gravity
all scale by that fraction. A zero fraction is skipped before checking the load
value, so land cells may retain missing ocean values without being counted as
missing water data.

The existing boolean water mask remains a hard include/exclude gate. Fractional
coverage is separate and auditable; invalid values or shape mismatches fail.

## Acceptance checks

- A 25% planar cell has exactly 25% area, mass, and gravity.
- Spherical and WGS 84 cells show the same linear scaling.
- A zero-fraction missing land cell is counted as zero-fraction, not as an ocean
  data gap.
- Negative, above-unity, and shape-mismatched fractions are rejected.

## Remaining coastline work

Production fractions must come from a versioned high-resolution coastline or
native ocean-product cell geometry. This API prevents all-water/all-land bias
but does not itself create the coastline fractions.
