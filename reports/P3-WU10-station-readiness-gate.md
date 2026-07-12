# P3-WU10 station-readiness gate

Status: implementation and unit validation complete; live FDSN inventory,
response and waveform checks pending network access.

FDSN channel metadata no longer suffices to admit a station. Each exact epoch
must separately record:

- a valid BH or LH vertical-plus-horizontal triplet;
- a fully verified response;
- downloadable waveform availability;
- permitted data use;
- real-time, near-real-time, archive-only, or unknown latency; and
- completed empirical-noise QC.

The audit separates retrospective-analysis stations from plausible operational
stations. An archive-only epoch can support noise/detectability analysis but is
not silently presented as deployable warning infrastructure. Every rejection
reason is preserved.

The empty repository manifest is intentional. Its one-station threshold is only
an inventory plumbing smoke gate, explicitly not the minimum scientific network
size. Network sufficiency is determined later by registered detection,
false-alarm, reliable-magnitude, outage, and Pareto analyses.
