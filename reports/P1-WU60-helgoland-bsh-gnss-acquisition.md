# P1-WU60 Helgoland BSH-HBMnoku and GNSS acquisition

Status: public model and raw GNSS acquisition complete; BSH structural audit
passes; paper-equivalent processed 2022 GNSS and IGETS gravity remain pending.

## BSH-HBMnoku

The official BSH Open Data Atom feeds and Germany Attribution License 2.0 were
frozen before download. The registered acquisition contains sea-surface height
from both grids used to cover the model domain:

- fine German Bight/western Baltic grid, approximately 900 m, 121 cycle files;
- coarse North Sea/Baltic grid, approximately 5 km, 121 cycle files.

All 242 NetCDF4/HDF5 files are stored only on AutoDL. They total 429,394,746
bytes; the deterministic file inventory SHA-256 is
`e5840fff8e56a8b11458b884da543b06bb1a1b617c7b7560f790f2a34b3f241c`.

The first structural audit exposed two files truncated during an earlier
duplicate-process race. The downloader was strengthened from a magic-byte check
to a complete HDF5 open plus `elev` dataset check, both files were removed and
downloaded again, and the inventory was regenerated. The clean audit then passed
all 242 files. Both grids have 2,880 contiguous 15-minute values in the
registered window, from 2022-01-26 00:15 UTC through 2022-02-25 00:00 UTC. The
source day encoding has a systematic 0.288-second offset, within the frozen
0.5-second rounding limit. The extra terminal cycle extends to 06:00 UTC and is
excluded by the registered trim.

## GNSS

The BKG EUREF archive contains the two public 30-second RINEX 3 compact-observation
series `HELG00DEU` (`14264M001`) and `HEL200DEU` (`14264M002`). All 62 daily files
for DOY 026–056 pass gzip payload checks. They total 209,861,943 bytes; the
deterministic inventory SHA-256 is
`2034a99ecca2ff43ca381ec9aeb6609989351ef70a2001782bc3564eb587dfe6`.

The paper cites the GFZ EPOS processed dataset DOI
`10.5880/GFZ.1.1.2023.001`. Its official archive was also obtained as a method
and format reference (SHA-256
`85e0c50a72d86cda0b48b087f425fa08a403c4a0e1f1dabd90cdcbefc16cd8e2`).
However, its official temporal extent ends on 2021-06-23, so it cannot be used as
the paper-equivalent processed coordinate series for the 2022 storm-surge
window. Reprocessing raw RINEX with an independently available solution would be
a new processing branch, not an exact reproduction of the cited GFZ EPOS series.

No gravity, deformation, correlation, or RMS-reduction target is marked as
reproduced by these acquisition results.
