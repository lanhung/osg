# LoadDef source and output-semantics audit

Audit date: 2026-07-12  
Status: exact v1.2.2 source/equations audited; Paper 1 CE provider scope passed
against published Martens et al. (2019) tables

## Primary sources inspected

- Official repository: <https://github.com/hrmartens/LoadDef>
- Green-function driver on the upstream main branch:
  <https://github.com/hrmartens/LoadDef/blob/main/LOADGF/GF/compute_greens_functions.py>
- Software paper DOI: <https://doi.org/10.1029/2018EA000462>

The exact `v1.2.2` tag resolves to commit
`b65493574f606b7d165a2d10fe862eda5b32f89a`; its archived source SHA-256 is
`77243146b260c6ff90d09cdeda6f721c6e8e3c003899614dab5e345c66611b5b`.
The GPL-3.0 source, PREM model, isolated MPI environment and generated bulk
tables remain on AutoDL.

## Direct source observations

The inspected `compute_greens_functions.py` main-branch source:

- accepts load Love numbers for vertical displacement, horizontal displacement,
  and gravitational potential;
- generates separate CE, CM, and CF output files;
- returns `gE`, `gE_cm`, and `gE_cf` elastic-gravity arrays;
- separately returns `g_N`, described by the output column as Newtonian gravity;
- writes normalized elastic gravity as `gE*(10^18*(a*theta))`; and
- writes displacement in `m/kg` while retaining normalized displacement columns.

The tag-specific equations identify `gE` as the combined displacement/free-air
and potential response, while `gN` is the separate direct Newtonian term.

## Binding project decisions

1. LoadDef `gE` enters the project's **combined elastic gravity** path unless a
   tag-specific equation audit proves a defensible decomposition.
2. Project direct attraction is calculated independently from the load grid.
   LoadDef `g_N` must not be added again to that budget.
3. CE, CM, and CF are separate products. One reference frame must be frozen in
   each experiment and encoded in provider metadata.
4. The normalized `gE` output is not SI acceleration per kilogram as written.
   An adapter must reverse the exact LoadDef normalization, with the code's
   angular convention and Earth radius, before creating a per-kilogram table.
5. Source input/output angles are degrees; harmonic evaluation and normalization
   convert them to radians. The project adapter reverses the normalization using
   radians and the source Earth radius.

## Scientific-use boundary

The published Martens et al. (2019) CE/CM/CF tables are reproduced exactly at
all 50 angles for the three fields consumed by the project provider: angle,
radial displacement and `gE`. Paper 1 freezes CE and may use this provider.
The broader twelve-column comparison retains small Love-number and tilt/strain
differences and remains failed; tilt and strain are not authorized. Paper 2 must
still evaluate reference-frame sensitivity against its observations.
