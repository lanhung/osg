# P3-WU13 discrete source-library inversion

Status: transparent reference inversion complete; validated Manila PEGS waveform
library and real covariance model remain unavailable.

The baseline ranks frozen source hypotheses by independent white-noise chi-square
over all included station samples. It returns the winning scenario's library
magnitude and rupture segment, improvement relative to the zero-signal model,
and delta chi-square to the second-best candidate. A best candidate that does not
beat the null is explicitly not treated as a detection.

If multiple hypotheses share the minimum chi-square, deterministic scenario-ID
ordering is retained only for serialization and `best_is_unique=false` prevents
the selected row from being reported as a uniquely identified source.

All hypotheses use identical stations, observations and masks. Duplicate scenario
identities, station mismatches, length mismatches and invalid noise scales fail
closed. Magnitude is discrete: the result cannot claim precision finer than the
scenario grid and does not interpolate between templates.

The audit records a versioned source-library ID, each hypothesis template source,
the shared sample interval, analysis-window start and duration, the resulting
decision time since origin, and every station noise-scale calibration source.
This makes time-dependent magnitude claims and noise-leakage review reproducible.

The output records sample interval, physical window duration, source-library ID,
per-hypothesis template provenance, and a calibration source ID for every station
noise scale. This makes it possible to reject templates or noise estimates that
were derived from the held-out event.

This is an interpretable lower-bound comparator for later likelihood or GNN
methods. Real evaluation still requires validated PEGS simulations, response-
corrected data, correlated/nonstationary noise, calibration of confidence, and
held-out rupture segments.
