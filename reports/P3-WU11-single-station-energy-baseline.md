# P3-WU11 single-station energy baseline

Status: leakage-safe scoring and evaluation interface complete; real PEGS
waveforms, instrument-response removal, passband selection and noise windows
remain unavailable.

The baseline computes RMS amplitude over fixed-length sliding windows. A window
is used only when every original sample passes the frozen inclusion mask; masked
samples are never compacted to create artificial continuity. Window length and
decision step are distinct and recorded.

The operational threshold is calibrated only on declared calibration quiet
windows. The same threshold is then applied without refitting to held-out quiet
windows and held-out event score sequences. Outputs include false alarms per
30-day month, rate resolution, event-level detection probability and the first
trigger index. Quiet and event identities cannot overlap.

RMS is intentionally a lower-bound baseline, not a PEGS detection claim. All
windows compared in a real experiment must share response-corrected units,
cadence, passband and preprocessing. The threshold must be calibrated with enough
quiet exposure to resolve the target false-alarm rate.
