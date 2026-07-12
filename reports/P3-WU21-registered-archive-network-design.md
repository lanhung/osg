# P3-WU21 Registered archive-network design

Status: open archive/noise-download design pass; operational and PEGS gates fail
by construction.

Registered experiment `P3-E002-archive-network-design` requires an exact match
of network, station, band, location and component triplet between the open
EarthScope archive and complete response structure. The first station-level
match was rejected and retained in registration history. The corrected output
reproduces on AutoDL with SHA-256
`508c2b09b0f769d69b68b07d76159401231328adb7c2849ecfab9367a27caaf8`.

Five LH three-component station epochs pass for historical noise evaluation:

- `HK.HKPS` (empty location; E/N/Z);
- `IC.QIZ` (location 10; 1/2/Z);
- `IU.DAV` (location 00; 1/2/Z);
- `MY.KKM` (empty location; E/N/Z); and
- `TW.KMNB` (empty location; E/N/Z).

Their common audited archive interval is 2020-01-01 through
2026-07-10T23:59:59 UTC. The outage design contains 1 full-network set, 5
four-station sets for the nominal 20% outage branch, and 10 three-station sets
for the nominal 40% branch. Historical-only SZP/DLV and response/archive-missing
YOJ/BAG/TWKB are retained separately.

This authorizes small, predeclared waveform downloads and response/QC work. It
does not establish current operation, real-time latency, PEGS detectability or
warning value.
