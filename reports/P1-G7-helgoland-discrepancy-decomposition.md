# Paper 1 G7 Helgoland discrepancy audit

Status: **pass with an explicit causal boundary** (2026-07-13)

Registered experiment P1-E009 audited the already admitted Helgoland component
series without changing the P1-E006 acceptance observable.

## Quantitative result

| Quantity | Result |
|---|---:|
| Combined elastic gravity / height | -2.266 nm s^-2 mm^-1 |
| Published comparison value | -2.684 nm s^-2 mm^-1 |
| Registered fractional difference | 15.56% |
| Direct gravity / height | -0.406 nm s^-2 mm^-1 |
| Direct / elastic RMS | 18.03% |
| Direct / elastic peak-to-peak | 18.09% |
| Diagnostic direct + elastic / height | -2.672 nm s^-2 mm^-1 |
| Diagnostic difference from publication | 0.45% |

Only the combined elastic value is authorized for the registered comparison.
The close diagnostic sum is reported to expose component scale; it cannot be
used to redefine the source paper's observable after seeing the result.

## What can and cannot be attributed

The remaining 15.56% registered difference is consistent with two declared
method changes: PREM/CE through LoadDef versus SPOTL/Gutenberg--Bullen, and a
30-day harmonic fit versus a three-year detiding analysis. These changes were
not varied independently in the available run, so their causal contributions
are confounded. No percentage is assigned to either source.

The audit therefore satisfies G7 by quantifying component magnitudes, preserving
the registered observable, and documenting the limit of attribution. It does
not claim observational validation: iGrav047 and a paper-equivalent processed
GNSS series remain unavailable.

Evidence:

- `experiments/paper1/P1-E009-helgoland-component-audit/registration.json`
- `experiments/paper1/P1-E009-helgoland-component-audit/metrics.json`
- `experiments/paper1/P1-E009-helgoland-component-audit/metadata.json`
