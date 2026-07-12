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
30-day month, rate resolution, the fraction of an event's score windows that
trigger, and the first triggering score index. Quiet and event identities cannot
overlap. The within-event trigger fraction is deliberately not called detection
probability; that probability must be estimated across independent held-out
events or noise realizations at each decision time.

RMS is intentionally a lower-bound baseline, not a PEGS detection claim. All
windows compared in a real experiment must share response-corrected units,
cadence, passband and preprocessing. The threshold must be calibrated with enough
quiet exposure to resolve the target false-alarm rate.
