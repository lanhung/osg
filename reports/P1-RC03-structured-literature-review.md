# P1-RC03 Structured literature review

Status: release literature-count, full-text and six-process coverage gates pass.

The Paper 1 bibliography now contains 46 uniquely keyed references. Every entry
is linked to `docs/paper1_literature_matrix.csv`, which records observable,
frequency band, instrument, source process, evidence type, manuscript role and
both supported and unsupported claim boundaries. Crossref/DOI metadata were
checked for all additions; 35 primary/review papers have a reviewed full text
and 11 retain the explicit `no` flag rather than being promoted from metadata or
abstract inspection.

The matrix contains at least three sources for each of tide, storm surge,
mesoscale eddy, internal wave, tsunami and submarine landslide. It also covers
terrestrial gravity fluctuations/Newtonian noise, SG and IGETS, preprocessing,
tidal and non-tidal ocean loading, absolute/atom gravimeters, atom gradiometers,
elastic loading, PREM, LoadDef and ellipsoidal geometry.

The Tang et al. entry now contains all 15 authors. No `and others` placeholder
remains. Instrument entries separate sensitivity, stability, self-noise and
site/environmental noise; facility announcements are not used as measured
curves. Harms and gravitational-wave literature support the general
environmental-gravity and observable framework, not a vertical-gravimeter noise
curve or an ocean-process detection claim.

Machine audit: `reports/p1_literature_matrix_audit.json`.
