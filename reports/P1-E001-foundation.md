# P1-E001 six-process foundation experiment

Status: reproducible engineering reference; not a paper result  
Runner commit: `bc04f17d62d48b2acbe8d6378a87b155e95a2584`  
Output SHA-256: `5c827b1d8c95be6999d3f0eb2695ba0e8a79ce3e08b6ddd6f7dc1f8df950c2ba`

## Purpose

This experiment proves that all six process primitives execute through one deterministic configuration and produce comparable frequency/direct-gravity metrics. Parameter values are engineering fixtures selected to exercise each model; they are not yet frozen literature priors and must not be cited as realistic ranges or detectability conclusions.

## Results

| Process | Dominant nonzero frequency (Hz) | Peak direct gravity (microgal) |
| --- | ---: | ---: |
| Tide | `2.2365e-5` | `38.707` |
| Storm surge | `6.6007e-6` | `65.118` |
| Translating SSH eddy | `4.8780e-7` | `8.311` |
| Compensated internal-wave dipole | `5.5556e-4` | `1.369` |
| Mass-balanced tsunami packet | `8.0840e-4` | `24.154` |
| Conserved point-pair landslide | `1.0929e-2` | `334.696` |

The internal-wave discrete net mass, tsunami net surface-mass amplitude, and landslide net mass anomaly are all zero in the machine-readable result. The landslide fixture also reports final vertical gravity-gradient change `-2.5433e-9 s^-2`.

## Reproduce

```bash
make reproduce PAPER=1 EXP=P1-E001-foundation
```

The dispatcher reruns the registered script and rejects any output whose SHA-256 differs. Scientific promotion of this experiment requires cited priors, elastic components, distance ensembles, instrument curves, uncertainty, and threshold sensitivity.

