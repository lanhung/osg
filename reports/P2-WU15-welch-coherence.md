# P2-WU15 mask-aware Welch coherence

Status: dependency-free reference implementation and physics tests complete;
production FFT parity and real event results pending.

The coherence calculation freezes sample interval, segment length, overlap,
detrending and window. Only complete segments whose every sample passes the
metric mask are used; used and discarded segment starts are preserved.

At least two valid segments are required because a single-segment
magnitude-squared coherence estimate is identically one wherever both spectra
are nonzero. Zero-power bins are reported as `None`. Values are bounded to [0, 1]
only for floating-point roundoff.

Physics tests verify unit coherence for identical repeated signals and near-zero
coherence when the cross spectrum cancels between equal-power opposite-phase
segments. This reference O(N²) implementation locks conventions; a production
FFT backend must reproduce it before replacing it for large data.

An explicit closed-band helper reports the unweighted mean of defined bins and
rejects bands containing no defined coherence values. It does not silently turn
zero-power bins into zero coherence.
