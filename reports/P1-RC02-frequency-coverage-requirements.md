# P1-RC02 Frequency-coverage requirements

Status: registered 1,446-record analysis complete on AutoDL.

P1-E008 reconstructs the exact P1-E006 direct-radial-gravity time series and
solves for the highest admissible lower band edge whose contiguous band through
the signal Nyquist frequency contains 50%, 75%, 90% or 95% of positive-frequency
energy. Constant detrending, a rectangular window and the existing one-sided
Fourier convention are frozen. The quantities are coverage requirements, not
SNRs or detection probabilities.

Median intrinsic low-frequency requirements are:

| Process | 50% (Hz) | 75% (Hz) | 90% (Hz) | 95% (Hz) | 1e-3/90% gap |
|---|---:|---:|---:|---:|---:|
| Mesoscale eddy | 3.886e-8 | 3.886e-8 | 3.886e-8 | 3.886e-8 | 25,731 |
| Storm surge | 4.244e-6 | 1.929e-6 | 7.716e-7 | 3.858e-7 | 1,296 |
| Internal wave | 2.202e-5 | 1.101e-5 | 1.101e-5 | 1.101e-5 | 90.83 |
| Tide | 2.207e-5 | 2.152e-5 | 2.147e-5 | 2.136e-5 | 46.58 |
| Submarine landslide | 4.923e-5 | 4.923e-5 | 4.923e-5 | 4.923e-5 | 20.31 |
| Tsunami | 2.626e-4 | 2.626e-4 | 2.626e-4 | 2.626e-4 | 3.808 |

The threshold sensitivity is process dependent. The Helgoland storm-surge
record changes by about an order of magnitude from 50% to 95%, whereas the
coarser transient designs often retain the same resolved bin across thresholds.
That equality is a finite-record spectral-resolution result, not evidence that
the thresholds are physically interchangeable.

Every admitted vertical-gravity anchor begins at 1e-3 Hz. Its low edge is above
the median 90% requirement by factors from 3.8 (tsunami) to 2.6e4 (eddy).
Consequently the prior coverage-limited conclusion is robust across the four
thresholds, while the required extension can now be stated quantitatively.

Registered metrics SHA-256:
`e9e169de96b7c7ec7349fbee8dcf5a1cc458bb7ca65ea5f9254e5d736de568d1`.
