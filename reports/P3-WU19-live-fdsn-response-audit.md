# P3-WU19 live FDSN response audit

Status: StationXML responses retrieved for 10 geographic-priority station pairs;
waveform availability, numeric deconvolution tests, latency and licensing remain.

The audit queried EarthScope `level=response` separately for QIZ, HKPS, DAV,
BAG, SZP, TWKB, KMNB, DLV, KKM and YOJ. All 10 pairs returned HTTP 200 and at
least one exact-epoch BH/LH three-component group with instrument sensitivity,
one or more response stages, and a PolesZeros/Coefficients/FIR/Polynomial
transfer-function structure on every component. Per-pair payload size and
SHA-256 are saved; approximately 2 MB of raw StationXML remain outside Git.

This verifies response structure, not successful response removal. Production
readiness still requires matching each waveform epoch to the exact response,
checking units, stage gains and normalization, running synthetic and real
deconvolution tests, confirming waveform holdings, and recording network terms,
acknowledgements and latency.
