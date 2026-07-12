# P1-E002 coverage-aware foundation detectability

Status: reproducible engineering reference; not a paper result  
Runner commit: `38a20c820016ae8b4c52f81cd11926aa7625daa1`  
Output SHA-256: `5b9deb990bb877d1e9ff8faeba3f2d760821a0ab3c5b9aff43f7cdbfc389eb52`

## Purpose

This experiment cross-compares the six engineering process fixtures with three traceable vertical-gravity noise anchors under required expected SNR `4.3717839` and minimum signal-energy coverage 90%. It tests the decision machinery and identifies missing frequency coverage; fixture amplitudes are not literature priors.

## Classification summary

| Process | AQG-A01 | FG5#228 | quiet-J9 iGrav self-noise |
| --- | --- | --- | --- |
| Tide | no coverage | no coverage | no coverage |
| Storm surge | partial (`9.66e-11`) | partial (`9.66e-11`) | partial (`9.66e-11`) |
| SSH eddy | no coverage | no coverage | no coverage |
| Internal-wave dipole | partial (`1.53e-29`) | partial (`1.53e-29`) | partial (`1.53e-29`) |
| Tsunami packet | partial (`0.2036`) | partial (`0.2036`) | partial (`0.2036`) |
| Landslide | partial (`0.8861`) | insufficient bins | model-detectable (`0.9541`) |

Numbers in parentheses are signal-energy coverage fractions, not probabilities. Only the landslide/iGrav fixture crosses both the 90% coverage gate and SNR threshold. AQG landslide band SNR is `19.06`, but 88.61% coverage fails the predeclared rule and is therefore unclassified. The very high partial-band iGrav tsunami SNR (`2405`) is likewise not a whole-signal result because only 20.36% of signal energy is covered.

Both gradient curves are explicitly excluded because their observable does not match vertical gravity.

## Reproduce

```bash
make reproduce PAPER=1 EXP=P1-E002-detectability-foundation
```

## Scientific implication

The present literature anchors are insufficient for hour-to-month ocean processes. Empirical low-frequency site-noise curves, long observation-time conventions, elastic responses, cited process priors, and distance ensembles are prerequisites for the real atlas. This negative coverage result is retained rather than filled by extrapolation.

