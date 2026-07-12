# P1-E004 six-process distance attenuation foundation

Status: reproducible engineering reference; not a paper result  
Runner commit: `27463308004eb66cd26d32501f7c4a7561519876`  
Output SHA-256: `1f1014525a47a754a296ee2e0393ed9b78dd079bf6cd3742fec2508499c12ece`

## Purpose

This experiment evaluates peak direct vertical gravity and peak absolute `Tzz`
for all six engineering process fixtures at seven vertical standoffs from 1 km
to 1,000 km. It validates geometry mutation, unit propagation, far-field decay,
and the future distance-panel data contract.

## Distance definition

- Tide, storm surge, eddy, and tsunami: height above the load/reference plane.
- Internal wave: height above the density-dipole centre.
- Landslide: height above the source–destination midpoint.

These definitions produce a controlled numerical comparison; they are not a
claim that all instruments occupy equivalent physical geometries.

## Endpoint attenuation

Ratio of the 1 km peak to the 1,000 km peak:

| Process | Vertical gravity ratio | `Tzz` ratio |
| --- | ---: | ---: |
| Tide | 199 | 1.01×10³ |
| Storm surge | 310 | 1.97×10³ |
| SSH eddy | 532 | 1.13×10⁵ |
| Internal-wave dipole | 1.01×10⁶ | 9.46×10⁷ |
| Tsunami packet | 6.89×10⁴ | 1.14×10⁷ |
| Submarine landslide | 1.53×10⁷ | 3.82×10¹⁰ |

The strong process-to-process differences reflect finite source size and mass
compensation. They are not universal power laws; near-field and transition
regions are included in the endpoint ratios.

## Reproduce

```bash
make reproduce PAPER=1 EXP=P1-E004-distance-attenuation-foundation
```

## Next gate

Replace engineering amplitudes/scales with cited scenario envelopes, add
elastic loading, and combine each distance series with empirical noise coverage
and observation-time assumptions before calling it a detectability atlas.
