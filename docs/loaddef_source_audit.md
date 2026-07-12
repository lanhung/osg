# LoadDef source and output-semantics audit

Audit date: 2026-07-12  
Status: partial upstream-main inspection; v1.2.2 artifact and equations not yet
fully audited

## Primary sources inspected

- Official repository: <https://github.com/hrmartens/LoadDef>
- Green-function driver on the upstream main branch:
  <https://github.com/hrmartens/LoadDef/blob/main/LOADGF/GF/compute_greens_functions.py>
- Software paper DOI: <https://doi.org/10.1029/2018EA000462>

The official repository identifies LoadDef as GPL-3.0, cites the 2019 software
paper, and lists v1.2.2 (2024-10-21) as the latest release. This browser-visible
evidence does not expose the tag commit or supply an artifact checksum, so those
fields remain unresolved.

## Direct source observations

The inspected `compute_greens_functions.py` main-branch source:

- accepts load Love numbers for vertical displacement, horizontal displacement,
  and gravitational potential;
- generates separate CE, CM, and CF output files;
- returns `gE`, `gE_cm`, and `gE_cf` elastic-gravity arrays;
- separately returns `g_N`, described by the output column as Newtonian gravity;
- writes normalized elastic gravity as `gE*(10^18*(a*theta))`; and
- writes displacement in `m/kg` while retaining normalized displacement columns.

These are observations about current upstream main, not proof that every line is
identical in v1.2.2.

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
5. The angular-distance convention remains unresolved: the source argument and
   file output are named `theta`, while the default numerical list and
   normalization must be checked against the manual/equations. No degrees-to-
   radians assumption is permitted from the name alone.

## Remaining acceptance evidence

- retrieve the exact v1.2.2 tag and record its 40-character commit;
- checksum the acquired source/archive and any generated Green-function table;
- read the v1.2.2 manual and software-paper equations for `gE`, `gN`, `theta`,
  signs, radius and normalization;
- freeze the Earth model and reference frame;
- reproduce the published Guo et al. Green-function comparison or another
  published LoadDef benchmark; and
- run the project scientific-use gate against the exact provider metadata.

Until all of these close, LoadDef remains selected but scientifically disabled.
