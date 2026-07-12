# P3-WU20 live FDSN archive availability audit

Status: EarthScope archive extents audited for 10 response-verified station
pairs; actual waveform download/QC, other data centres and SeedLink remain.

The official FDSN availability `extent` service returned three-component archive
coverage for 8 of 10 station pairs. Six pairs—QIZ, HKPS, DAV, KMNB, KKM and
YOJ—have a common three-component latest sample within seven days of the
2026-07-12 retrieval. SZP ends in January 2021 and DLV in October 2023 within
the EarthScope holdings. BAG and TWKB return 404 despite valid StationXML
responses, demonstrating that metadata presence does not imply this archive
holds the waveform.

Each compact result preserves the exact request, raw JSON hash, common triplet
extent, sample rate, open/restricted flag and maximum timespan count. Raw
availability documents remain outside Git.

“Recent archive sample” is not “real-time capable.” The next steps are small
permitted waveform downloads for fixed calm and high-noise dates, gap/response
QC, queries to relevant non-EarthScope centres for BAG/TWKB and others, and a
separate SeedLink latency/operational audit where terms permit.
