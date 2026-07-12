# P2-WU04 gridded sea-level direct-gravity forward path

Status: implemented for spherical and WGS 84 geometry; elastic path remains gated

## Contract

Each timestamp carries a complete sea-level-anomaly grid. The adapter converts
metres of SSH to signed surface density with explicit water density, applies
masks and partial coastal-cell fractions, then computes local-up direct gravity.
It returns the time series together with included signed mass and effective area.

Time order is strict and no temporal/spatial interpolation occurs. Missing-data
policy is delegated explicitly to the audited grid kernel.

## Acceptance checks

- Zero, positive and negative uniform SSH scale gravity and mass linearly.
- Zero-fraction land cells may contain missing ocean values.
- WGS 84 and mean-radius spherical results are distinct but agree within 1% for
  the regional validation patch.
- Duplicate times and unknown geometry fail.

## Scientific boundary

This completes the direct-water-attraction branch needed for CMEMS or regional
storm-surge fields. Deformation and internal-potential responses remain separate
and must enter only through a validated load Green-function provider. Dataset
variable semantics, tides, mean removal and inverse-barometer double counting
must be resolved before event use.
