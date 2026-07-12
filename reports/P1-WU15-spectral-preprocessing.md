# P1-WU15 spectral detrending and windows

Status: implemented; awaiting independent human review

## Frozen options

- Detrending: none, constant, or least-squares linear trend in physical seconds.
- Windows: rectangular or periodic Hann.
- Fourier amplitude uses the windowed residual series.
- PSD divides by window power gain `mean(w^2)`.
- Peak-amplitude recovery divides by coherent gain `mean(w)`.
- Equivalent noise bandwidth in bins is `mean(w^2) / mean(w)^2`.

For the periodic Hann window, coherent gain is 0.5, power gain is 0.375, and ENBW is 1.5 bins.

## Predefined acceptance checks

- Periodic-Hann gains and ENBW equal their analytic values.
- Integrated PSD equals normalized window-weighted record mean square within relative `2e-14`.
- Coherent-gain correction recovers a bin-centred sinusoid's peak amplitude within relative `2e-14`.
- Constant detrending and the legacy mean-removal alias are identical.
- Linear detrending removes a pure affine record to numerical roundoff and recovers its slope.
- Unknown/ambiguous preprocessing requests are rejected.

## Result

All checks pass. Gap handling, irregular timestamps, resampling anti-alias filters, Welch segment averaging, confidence intervals, and nonstationarity remain data-quality work units.

