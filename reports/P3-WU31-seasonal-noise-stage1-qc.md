# P3-WU31 Seasonal noise stage-1 QC

Status: retrieval and response-QC yield gates pass; environmental promotion
gate fails; no noise label or PEGS claim is authorized.

Registered experiment `P3-E003-seasonal-noise-stage1` processed the eight
calendar-selected days on AutoDL. EarthScope returned 38 of 40 station-day
requests. Thirty-five of 40 records passed exact channel, gap/overlap and
response-removal QC.

All five failures belong to MY.KKM: HTTP 404 on 2023-08-15 and 2025-05-15;
three gaps/overlaps on 2023-02-15 and 2023-05-15; and 756 gaps/overlaps on
2025-11-15. The failures are retained and are not replaced from observed noise.
Every date has at least four passing stations, so the frozen six-of-eight
response-QC yield minimum passes. Three dates have a complete five-station
network: 2023-11-15, 2025-02-15 and 2025-08-15. Their maximum absolute
off-diagonal vertical correlations are respectively 0.0157, 0.3077 and 0.0617.
These values are descriptive and unclassified.

The companion catalogue audit finds earthquake-screen candidates in seven of
eight dates and no regional IBTrACS overlap. Only 2025-08-15 passes both frozen
catalogue layers, and even that date remains pending local weather, sea state,
microseism and waveform-transient review. Thus the quiet-label count remains
zero and the environmental promotion gate fails. Threshold calibration,
false-alarm estimation, PEGS detectability and GNN training remain unauthorized.

The compact registered metrics SHA-256 is
`b63c7e7598b234abaeae07de221cf08638ea8d350c1a88ca289b14d939d9ba8b`.
Raw MiniSEED and StationXML remain on AutoDL.
