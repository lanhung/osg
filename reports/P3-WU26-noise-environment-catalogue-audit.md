# P3-WU26 noise-environment catalogue audit

Status: earthquake and regional tropical-cyclone layers complete for five pilot
windows; zero windows are authorized as quiet.

The frozen audit queried the USGS FDSN event service from 12 hours before each
window through its end at magnitude 4.0 and above. A conservative candidate is
retained when a magnitude 6.0 global event, or a magnitude 4.5 event within
1000 km, has a 2.5--4.0 km/s surface-wave arrival and three-hour coda overlapping
the station window. This is a screening rule, not a physical contamination
measurement. Raw GeoJSON remains on AutoDL; exact URLs and response SHA-256
values are versioned.

Three windows pass both catalogue layers: 2024-02-15, 2024-05-15 and
2025-05-15. The Yagi stress window contains two regional earthquake candidates
and overlaps IBTrACS Yagi. The 2025-02-15 replacement contains two Philippine
earthquake candidates. These two windows must not be used as quiet calibration
or held-out noise under the frozen rule.

All five labels remain `pending_weather_sea_state_and_waveform_review`. ERA5 or
equivalent station-local pressure/wind, regional sea state, and waveform
transient/microseism review are still required. Consequently the audit improves
candidate triage but does not yet authorize threshold calibration, false-alarm
estimation, PEGS detectability or GNN training.
