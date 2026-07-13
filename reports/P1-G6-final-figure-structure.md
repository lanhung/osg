# Paper 1 G6 final figure structure

Status: **pass** (2026-07-13)

The main manuscript now uses five figures with one scientific narrative:

1. observable and evidence framework;
2. process frequency support and admitted instrument evidence;
3. process-specific lower-frequency requirements;
4. direct radial-gravity amplitude versus standoff;
5. physical closure and Helgoland component validation.

The process--instrument matrix and parameter-sensitivity envelopes remain
versioned as Supplementary Figures S1 and S2. This prevents an all-partial
matrix from carrying the central result and keeps scenario extrema distinct
from probability intervals.

## Observable controls

- Every main-figure row is recorded in
  `data/manifests/paper1_observable_ledger.csv`.
- Figures 2--4 are explicitly direct radial gravity.
- Figure 5 stores direct gravity, combined elastic gravity and displacement
  separately.
- The direct-plus-elastic Helgoland value is hatched and labelled diagnostic;
  it is not used as an acceptance comparison.
- Gravity gradient remains a separate supplemental observable.

The authoritative paths and SHA-256 values are recorded in
`papers/paper1_atlas/figure_manifest.json` and
`reports/figures/paper1/p1_figure_manifest.json`.
