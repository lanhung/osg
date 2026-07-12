# P2-WU10 SG calibration and instrument-step ledger

Status: implementation and unit validation complete; real calibration and
maintenance records pending data access.

Feedback voltage calibration now requires a versioned ID, SI factor and standard
uncertainty, voltage/gravity offsets and uncertainty, UTC validity interval, and
source. Factor and offset uncertainty are propagated sample by sample; a negative
instrument factor is preserved rather than normalized away.

Persistent instrument jumps are corrected only through explicit decisions that
record a unique ID, the index of the later sample, the observed step in SI units,
the evidence source, and the rationale. The output retains the full cumulative
removed-step series and the ordered decision IDs. Multiple decisions at one
sample, index-zero corrections, out-of-range decisions and zero-sized steps are
rejected.

This module deliberately does not estimate a calibration factor or discover and
classify steps. Candidate discontinuities remain outputs of the separate quality
summary; calibration comparisons, instrument logs and human-reviewed decisions
must populate the models before they can alter observations.
