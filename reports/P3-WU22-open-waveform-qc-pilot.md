# P3-WU22 Open waveform QC pilot

Status: response/QC pipeline demonstrated on real open archives; no threshold,
PEGS detectability or operational claim is authorized.

The first predeclared acquisition requested three simultaneous six-hour windows
for the five exact response/archive-matched LH station triplets in `P3-E002`.
Thirteen of 15 requests returned MiniSEED. Twelve records passed exact channel,
zero-gap, three-trace and acceleration-response-removal gates. KKM returned 404
for the February and May 2024 windows, and KMNB had three gap/overlap entries in
the May window.

The Yagi-period candidate is the only original complete five-station window. Its
start-time span is 39.1 microseconds, below the frozen 0.001-sample tolerance at
1 Hz, so a descriptive cross-station correlation matrix is permitted without
resampling. The off-diagonal raw response-corrected correlations are small
(-0.030 to 0.039), but this is an unclassified six-hour diagnostic and is not a
covariance model or evidence of station independence.

Two replacement dates were chosen only because of retrieval/gap failures, not
after inspecting noise amplitudes. Nine of ten replacement requests succeeded
and passed response QC. The February 2025 replacement supplies a second complete
five-station window; KKM again returned 404 for May 2025.

Across the original and replacement pilots, 22 of 25 requests were retrieved and
21 passed response QC. Raw MiniSEED and StationXML remain on AutoDL. Compact
queries, failures, hashes and diagnostic metrics are versioned. The original
acquisition and diagnostic-QC SHA-256 values are
`61706be59fc297f713ac132d8f833f8e6ad0d556e2891786c5f5f980cc5f5c72`
and `35c5a8f71be9556dfb670eec8222c2de4188e3cf3a7c4b42cfeed3e69e1b3b75`.
The replacement acquisition and QC hashes are
`90af4256c3f46c399a702931eb22bf43c0de56440ef20190811da500f3312394`
and `fb20840fc6a6b3c85cd1ab78b31f5e278c901b98583c1999106c79e2fd1697ad`.

Remaining gates are independent earthquake/weather/transient labels,
network-specific licences/citations, much longer exposure at the target false
alarm rate, and frozen train/validation/held-out date sets.
