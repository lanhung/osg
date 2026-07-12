# P1-WU54 Haikou reproduction contract and novelty audit

Status: VOR targets and method contract frozen; observational inputs restricted;
current executable audit status is `pending`.

The 2026 VOR differs numerically from the 2025 preprint, so the registered targets
use only VOR results: CMEMS/MPIOM maximum NTOL variations 2.6/3.0 μGal,
observation correlations 0.83/0.81, model–model correlation 0.87, uncorrected RMS
0.81 μGal, and CMEMS/MPIOM-corrected RMS 0.50/0.54 μGal (38%/34% reductions).
The December 22 absolute load state is stored separately and cannot be confused
with the 2.6 μGal variation range.

The study window is 22 December 2023 through 30 April 2024. It was deliberately
chosen as the dry season to reduce rainfall/groundwater interference. It contains
no named typhoon-event analysis or event windows. Therefore it occupies general
South China Sea NTOL modelling/correction, but does **not** pre-empt Paper 2's
event-resolved typhoon attribution claim.

The method contract freezes the 1 Hz to hourly SG processing, FG5 calibration
window, WDD, FES2014b, local atmospheric admittance and its stated limitation,
EOPC04, hydrology parameters, CMEMS product/domain/grid, SPOTL Gutenberg–Bullen
elastic loading, separate curved-Earth Newtonian attraction, and MPIOM
displacement-to-gravity conversion.

The article states that SG and GNSS observations are not public. CMEMS and MPIOM
sources are identified, but exact historical product versions/paths and
checksums remain absent. Consequently all eight targets are pending. Model-only
reproduction may proceed after product audit; observation correlation/RMS cannot
be reproduced without author collaboration.

Run:

```bash
python3 scripts/evaluate_haikou_reproduction.py
```
