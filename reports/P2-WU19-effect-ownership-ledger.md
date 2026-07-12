# P2-WU19 environmental-effect ownership ledger

Status: executable metadata gate complete; current CMEMS/ERA5 composition
correctly fails closure.

Every required physical effect must have exactly one `included` source and no
other source whose status is `unknown`. The audit distinguishes missing owner,
duplicate owner and ambiguous possible overlap.

The frozen Paper 2 ledger currently assigns the separate inverse-barometer model
to ERA5 while the exact historical CMEMS product remains `unknown` for the same
effect. Therefore `closure_ready=false`. This is intentional: adding the ERA5
response now could double count pressure-driven ocean mass already present in
CMEMS.

The resolution is binary and evidence-based. After auditing the exact CMEMS
dataset, either mark its inverse-barometer representation `excluded` and retain
the ERA5-derived response, or mark it `included` and remove the separate response.
Changing a time-series component ID without closing this metadata ambiguity is
not sufficient.

Run:

```bash
make audit-effects
```
