# P1-WU35 tabulated load Green-function provider

Status: interchange adapter implemented; no physical table enabled

## Contract

The adapter reads versioned JSON tables already normalized per source kilogram,
preserves deformation gravity, internal-mass gravity, and vertical displacement
as distinct columns, and linearly interpolates in angular distance. It refuses
all extrapolation and rejects non-monotonic or mismatched tables.

## Acceptance checks

- Exact nodes and signed component interpolation are correct.
- Values outside the audited table range fail closed.
- Metadata carries provider version, Earth model, source, and normalization.
- Component arrays must match a finite, strictly increasing distance grid.
- The adapter satisfies the existing provider protocol and convolution path.

## Scientific gate

The test table is analytic and explicitly nonphysical. No LoadDef data may enter
this interchange format until `P1-WU34` resolves the exact `gE` semantics,
reference frame, Earth model, distance normalization, release commit, and source
checksum. The adapter is infrastructure, not elastic-loading validation.
