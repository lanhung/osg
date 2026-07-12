# P2-WU06 stepwise SG correction chain

Status: implemented and unit-tested

## Contract

After the physical-effect collision audit, corrections are applied in declared
order. Every stage stores its input series, exact removed component, output
series, component ID, stage index and peak absolute contribution. The final
sequential residual is cross-checked against direct all-component subtraction.

This supports the required correction waterfall and prevents a black-box
“corrected gravity” product from hiding which stage removed an event-scale peak.

## Boundary

The chain performs arithmetic, not scientific classification. Calibration,
solid tide, ocean-tide loading, polar motion, atmosphere, hydrology, drift and
NTOL models must each arrive as independently sourced components with explicit
units and effect IDs. Filter transients and uncertainty propagation remain to be
added before real SG processing.
