# P2-WU03 gravity-budget component ledger

Status: implemented and unit-tested

## Contract

Every correction time series carries a unique component ID, one or more unique
physical-effect IDs, source, SI values, and a flag stating whether it was already
applied to the input. Residual assembly subtracts components sample by sample and
reports numerical closure.

Two selected components may not claim the same physical effect. A CMEMS ocean
series labelled as containing `ocean_inverse_barometer` therefore cannot be
combined with a separate ERA5-driven inverse-barometer series. Inputs already
corrected for NTOL likewise cannot silently receive NTOL a second time.

## Acceptance checks

- Solid tide, atmosphere and ocean fixtures close exactly to the observed series.
- Duplicate inverse-barometer ownership fails with both component IDs exposed.
- Pre-applied components, duplicate IDs, invalid values and length mismatches fail.
- Direct ocean, elastic ocean and atmosphere remain distinct effect IDs.

## Use

Product metadata must determine the effect IDs before any event residual is
assembled. Unknown product physics is a blocking audit state, not permission to
assign a convenient label.
