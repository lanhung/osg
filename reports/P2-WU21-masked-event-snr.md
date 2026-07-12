# P2-WU21 mask-aware event SNR

Status: non-overlapping masked transient-SNR reference implementation complete;
real station PSDs, event bands, mismatch and trials calibration pending.

The event template is divided into fixed, non-overlapping complete segments.
Only segments whose every sample passes the frozen metric mask are transformed;
the implementation never joins samples across a gap. Segment matched-filter
SNRs use the project's one-sided PSD convention and combine as the square root
of summed squared SNR. Rejected segment starts and trailing samples that cannot
form a complete segment are reported.

Non-overlap is required here because overlapping segments would count template
energy more than once. The output is a ranking/diagnostic metric, not a detection
decision: a real claim still requires a station-specific noise PSD, frozen event
band, template-mismatch study, empirical threshold, and trials-factor/false-alarm
calibration.
