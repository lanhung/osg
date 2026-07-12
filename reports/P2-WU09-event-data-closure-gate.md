# P2-WU09 event/station data-closure gate

Status: implementation and unit validation complete; real availability records
pending station-owner/IGETS access.

The Paper 2 gate now evaluates every event–station pair rather than counting
named typhoons alone. A pair is eligible for full physical attribution only if
it has:

- Level 1 or explicitly equivalent raw-enough gravity;
- at least the caller-frozen gravity coverage fraction (default 95%);
- colocated pressure, calibration and instrument-state records;
- sea-level anomaly and precipitation/hydrology support; and
- a typhoon track for typhoon windows.

Only eligible pairs are passed into the leakage-safe event-design audit. Level 3
residuals are explicitly ineligible for the full attribution claim, although
they can still support a narrower case or model-evaluation branch. Missing
declarations and every exclusion reason remain in the audit output.

The default 95% coverage threshold is a pre-analysis engineering default, not a
claim that short gaps are harmless. Real records still require gap-length,
timing, spectral and correction-stage sensitivity checks.

The repository manifest is connected to the audit with:

```bash
python3 scripts/audit_paper2_data_gate.py
```

A final `go_full_attribution` or `no_go_full_attribution` is emitted only after
the manifest's `decision_status` is deliberately changed from `draft` to
`frozen`. The current empty manifest correctly emits `pending_no_event_windows`.
