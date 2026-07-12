# P1-WU14 transient and periodic SNR

Status: implemented; awaiting independent human review  
Noise convention: positive one-sided PSD in signal-units squared per hertz

## Definitions

Transient/template SNR uses

```text
rho^2 = 4 integral |s_tilde(f)|^2 / S_n(f) df
```

with a trapezoidal integral over explicitly selected sampled bins. DC is excluded by default. No PSD interpolation or out-of-band extrapolation is implicit.

For an exactly modelled sinusoid whose stated amplitude is peak (not RMS),

```text
rho = |A_peak| sqrt(T_coherent / S_n).
```

## Predefined acceptance checks

- A bin-centred time-domain sinusoid gives the same SNR through the DFT/matched-filter path and the periodic closed form within relative `2e-14`.
- SNR is linear in signal amplitude, inverse square-root in noise PSD, and square-root in coherent time.
- A band excluding the signal returns numerical zero.
- Zero signal returns zero.
- Non-positive PSD/time, invalid coherence fraction, non-contiguous/undersampled bands, and inconsistent array shapes are rejected.

## Result

All checks pass. Detection claims still require a separately frozen threshold and false-alarm convention, realistic nonstationary noise, template mismatch, and trials-factor treatment; `SNR > value` alone is not yet a decision rule.

