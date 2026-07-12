# P3-WU12 multi-station template baseline

Status: aligned independent-noise reference statistic complete; validated PEGS
templates, response-corrected network data and real cross-station noise remain.

For every sliding window the baseline evaluates the signed, noise-weighted
network inner product and divides by template norm. Station-specific waveform
polarity is preserved. Equal coherent stations give the expected square-root-of-
station-count gain under the stated independent white Gaussian reference model.

Station series, templates, noise scales and optional inclusion masks must have
exactly matching station identities. If any participating station has a masked
sample, the whole candidate network window is discarded without temporal
compaction. Outage experiments must instead define a new fixed participating
station subset so changing network normalization is explicit.

The analytic noise interpretation is only a reference. Operational thresholds
must use the same held-out real-noise false-alarm audit as the single-station
baseline, particularly because microseism and typhoon noise violate temporal and
cross-station independence.
