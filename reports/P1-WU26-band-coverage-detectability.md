# P1-WU26 frequency-coverage-aware detectability

Status: implemented; awaiting independent human review

## Decision rule

A vertical-gravity signal is Fourier transformed under the frozen convention. The fraction of positive-frequency signal energy lying inside an instrument curve's declared band is computed before SNR classification.

- fewer than two covered bins: `no_frequency_coverage`;
- zero signal: `zero_signal`;
- coverage below the frozen minimum (default 90%): `partial_band_not_classified`;
- adequate coverage and SNR above/below threshold: model-qualified detectable/not-detectable.

SNR may still be reported for a partial band, but it cannot be promoted to a whole-signal classification. No curve is extrapolated.

## Predefined acceptance checks

- An in-band bin-centred sinusoid has full energy coverage and the analytic white-noise SNR.
- A disjoint curve yields no SNR and unknown classification.
- Two equal-energy tones with only one inside the band produce 50% coverage and remain unclassified even at arbitrarily high local-band SNR.
- Zero signal, observable mismatch, units, thresholds, and coverage bounds are validated.

## Result

All checks pass. This gate is expected to mark many hour-to-month ocean processes “unknown” until low-frequency empirical station-noise curves are acquired. That is a scientific data gap, not permission to extend a convenient white-noise anchor.

