# P1-WU73 temporal and spectral convergence decision

Status: P1-E011 completed on AutoDL; the central 0/1,446 classification result
is retained, while exact native-bin lower-edge headlines are superseded.

The preregistered production run executed on
`autodl-container-7fb444a9ae-9b4ed319` from 2026-07-20T10:16:59Z through
10:18:39Z. The checksum-registered output is
`experiments/paper1/P1-E011-temporal-spectral-convergence/metrics.json`, SHA-256
`b37ff38278cb231e6b9e5ea0c41ccd7b4f7f401f6d052f303561a0396afc2fbf`.

## Release decision

- Dense, boundary-aware 90% coverage passes: **0 of 1,446**.
- Process-median finite-DTFT grid convergence: **pass for all six processes**.
- Representative analytic-source cadence convergence: **pass for all five
  regenerable process families**. The hourly storm archive was not interpolated.
- Window stability: **pass** for tide and internal wave; **window limited** for
  mesoscale eddy, storm surge, tsunami and submarine landslide.

Consequently P1-E006-v2 is not required. P1-E006 remains the immutable source
ensemble and its no-classification conclusion is retained. P1-E008 native-bin
values remain a historical numerical result but are no longer interpreted as
process-intrinsic measurement requirements.

## Converged and window-conditioned estimates

At 90% unweighted finite-record spectral-energy coverage, the exact-cycle tide
windows give median lower edges of `2.157e-5`, `2.194e-5` and `2.216e-5 Hz`;
the 2-, 4- and 8-period internal-wave windows give `1.817e-5`, `1.992e-5` and
`2.101e-5 Hz`. Their largest-two-window changes are 1.00% and 5.20%, below the
fixed 10% gate.

The four remaining branches change materially with record definition:

| Process | Window design | Median 90% lower-edge range (Hz) | Diagnostic |
|---|---|---:|---|
| Mesoscale eddy | +/-4, +/-6, +/-8 characteristic times | `1.407e-8`--`2.793e-8` | `f_low T = 0.71875`; window limited |
| Storm surge | fixed 7, 14 and 30 day UTC windows | `7.837e-7`--`3.488e-6` | `f_low T = 2.03`--`2.23`; archive cadence retained |
| Tsunami | 4, 8 and 12 packet-scale padding | `5.990e-5`--`9.903e-5` | `f_low T = 0.375`--`0.469`; window limited |
| Submarine landslide | 0.5, 1 and 2 transition-duration padding | `7.764e-6`--`1.846e-5` | `f_low T = 0.375`--`0.391`; window limited |

Every value remains below the most permissive reviewed curve edge of
`5e-4 Hz`. These ranges are scenario/window diagnostics, not universal process
constants, detection probabilities, or SNR contributions.

## Required manuscript action

The journal revision must lead with the stable common-support conclusion and
must not retain the old `3.89e-8`--`2.63e-4 Hz` headline as an instrument-design
requirement. Figures and Supplementary tables must distinguish the two stable
process estimates from the four window-conditioned ranges and keep the three
instrument reference bands separate.
