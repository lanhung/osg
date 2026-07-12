# P1-WU13 Fourier and one-sided PSD convention

Status: implemented; awaiting independent human review  
Reference implementation: dependency-free direct DFT (`O(N^2)`)  
Window: none; mean removal is explicit and off by default

## Frozen convention

For `N` samples separated by `dt`, record duration is `T=N dt`, frequency spacing is `df=1/T`, and

```text
X_k = dt sum_n x_n exp(-2 pi i k n/N).
```

The one-sided periodogram is `|X_k|^2/T` at DC and even-record Nyquist, and `2|X_k|^2/T` for positive-frequency bins whose negative partners are omitted. It has input-units squared per hertz. Its discrete integral equals record mean square.

## Predefined acceptance checks

- Parseval/mean-square closure for even and odd record lengths within relative `2e-14`.
- A bin-centred sinusoid has transform magnitude `A T/2` and mean square `A^2/2`.
- A constant record occupies DC; explicit mean removal produces zero.
- Frequency spacing and even-record Nyquist follow `df=1/T` and `f_N=1/(2dt)`.
- Short, non-finite, or non-positive-interval inputs are rejected.

## Result

All checks pass. A production FFT backend, detrending, window coherent gain/noise bandwidth, gaps, resampling, and spectral-estimation uncertainty must reproduce or explicitly extend this reference convention.

