# P1-E003 coverage-aware gravity-gradient foundation detectability

Status: reproducible engineering reference; not a paper result  
Runner commit: `c4354f889a72dbfdc63593125f0260b226d301a2`  
Output SHA-256: `5af4e7b56d3e054e8e4326a8ffcc230a04f7d1e976635d849d7ba21e2949ebe2`

## Purpose

This experiment cross-compares the six engineering process `Tzz` fixtures with
two traceable gravity-gradient noise anchors under required expected SNR
`4.3717839` and minimum signal-energy coverage 90%. It validates the gradient
decision path; fixture amplitudes are not literature priors.

## Classification summary

| Process | McGuirk atom gradiometer | GOCE EGG design anchor |
| --- | --- | --- |
| Tide | no coverage | no coverage |
| Storm surge | partial (`9.66e-11`) | no coverage |
| SSH eddy | no coverage | no coverage |
| Internal-wave dipole | partial (`1.54e-29`) | partial (`1.24e-29`) |
| Tsunami packet | partial (`0.3207`) | partial (`0.000721`) |
| Landslide | covered but below threshold (`SNR=2.885`) | model-detectable (`SNR=2254`) |

Parenthesized values are signal-energy coverage fractions unless marked as
SNR. Only the landslide/GOCE fixture crosses both the 90% coverage gate and the
predeclared SNR threshold. This is an engineering-model classification, not a
claim that a satellite mission can observe the specified local event geometry.

All three vertical-gravity curves are explicitly excluded because their
observable and ASD units do not match gravity gradient.

## Reproduce

```bash
make reproduce PAPER=1 EXP=P1-E003-gradient-detectability-foundation
```

## Scientific implication

As for vertical gravity, the current anchors do not cover most long-period
ocean-process energy. Site- and platform-specific empirical gradient noise,
realistic observation geometry, cited process priors, and parameter ensembles
are required before this matrix can become part of the atlas.
