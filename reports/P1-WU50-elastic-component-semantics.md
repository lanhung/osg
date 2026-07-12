# P1-WU50 elastic Green-function component semantics

Status: interface correction and unit validation complete; LoadDef source audit
and scientific benchmark still pending.

The load interface previously required every provider to return separate
deformation-gravity and internal-mass/potential terms. That contract was too
strong for a source that publishes only one combined elastic-gravity Green
function: an adapter could satisfy the software API only by inventing a split.

The interface now has two mutually exclusive semantics:

1. `decomposed_deformation_and_internal_mass`, which may use the existing
   separated convolution path; and
2. `combined_elastic_gravity`, which returns direct attraction, combined elastic
   gravity, and displacement without exposing fictional subcomponents.

Crossing these paths raises an error. A combined response has no deformation or
internal-mass attributes, so downstream code cannot accidentally label one
combined value as either component.

This does not waive Paper 2's desired physical decomposition. It means that such
a decomposition may be claimed only if the selected source equations and output
definitions genuinely provide it, or if an independently validated calculation
supplies the missing terms. Until the LoadDef `gE` source/equation audit is
complete, its eventual adapter must use combined semantics.
