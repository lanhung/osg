# P3-WU27 seasonal long-noise acquisition plan

Status: stage 1 dates and promotion gates frozen before acquisition.

Stage 1 requests eight exact UTC days spanning February, May, August and
November in separate 2023 calibration and 2025 held-out years. Five stations
give 40 requested station-days. Dates follow a calendar rule and were not chosen
from waveform amplitude or weather. Raw MiniSEED remains on AutoDL.

This stage measures retrieval, response/gap-QC and environmental-label yield; it
cannot support a one-false-alarm-per-30-day claim because each split contains
only four days. Expansion is conditional on at least four stations passing in
six of eight days and completion of all environmental layers. A production
split needs at least 32 accepted days independently for calibration and held-out
evaluation. Failed dates may not be replaced based on observed noise amplitude.

The AutoDL acquisition retrieved 38 of 40 requests (21,951,488 bytes). Both
failures are retained as KKM HTTP 404 responses, on 2023-08-15 and 2025-05-15.
Every day therefore has at least four retrieved stations, so the retrieval part
of the stage gate passes. Response/gap QC and all environmental labels remain
separate gates.

Response processing then passes 35 of 40 records. All five failures are KKM:
the two retained 404 responses plus gap/overlap failures on 2023-02-15,
2023-05-15 and 2025-11-15. Every date still has at least four response-QC
stations, so the predeclared six-of-eight promotion minimum passes; three dates
have a complete five-station network. This remains unclassified diagnostic
exposure, not a threshold or false-alarm dataset.
