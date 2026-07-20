# P1-WU72 Journal revision and E011 audit

Status: revision infrastructure complete; P1-E011 executed and finalized;
author affiliations verified; archival DOI and author declarations pending.

The repository did not contain the separately circulated Journal of Geodesy
source described by the review. Its release workflow compiled only
`papers/paper1_atlas/main.tex`, so a clean technical-preprint build could not
detect citation failures introduced in an external journal copy. The new
`papers/paper1_journal_of_geodesy/` package selects a precise title containing
`Direct`, shares the maintained scientific body and bibliography, provides a
standalone Supplementary Information source and has its own fail-closed build.

The build refuses release unless:

- P1-E011 has finalized checksum-verified metadata;
- all author affiliations, corresponding-author details and required ORCIDs are
  verified;
- a real archival DOI is present;
- main and Supplementary PDFs compile through the full LaTeX/BibTeX cycle with
  no undefined citations or references;
- no internal draft or DOI-placeholder marker is present.

Four Supplementary tables are now generated directly from configs and frozen
metrics: process parameters, the complete 1,446-record composition and temporal
resolution, 50/75/90/95% frequency requirements, and instrument evidence. The
Valencio article number is corrected to 103126; Antokoletz volume 236 is dated
2024 and Dullaart volume 54 is dated 2020. DOI URLs are stored with these
corrected records.

The scientific code audit confirmed that the original implementation used a
two-native-bin requirement because trapezoidal integration needs an interval.
It returned the same `no_frequency_coverage` status both when source Nyquist lay
below a curve and when a common interval was under-resolved. A new non-invasive
frequency-support audit reports record duration, native spacing, source
Nyquist, curve bounds, native overlap-bin count and distinct resolution status.
The frozen P1-E006 default output remains unchanged by regression test.

P1-E011 was committed and then preregistered before production. It fixes:

- finite-record DTFT sampling at 1x, 4x, 16x and 64x zero-padding factors;
- 16x--64x 5% grid-convergence comparison;
- 1x, 2x, 4x and 8x analytic-source cadence comparison with a 4x--8x 5% gate;
- integer-cycle tide windows, eddy half-widths of 4/6/8 characteristic times,
  internal-wave windows of 2/4/8 periods, tsunami padding of 4/8/12 scales,
  slide padding of 0.5/1/2 transition durations and exact 7/14/30-day storm
  windows without upsampling the hourly archive;
- boundary-aware integration at instrument edges;
- separate source-support, grid-resolution and energy-coverage status counts.

An initial pending registration contained a mistyped non-integer tide duration.
It was corrected to exact 14, 27 and 58 M2-cycle windows and the preregistration
hash was updated before any production execution. The history is retained.

Production ran on AutoDL on 2026-07-20 after the registered code was imported
into an isolated worktree without modifying the server's existing dirty working
copy or active jobs. The checksum-registered result is summarized in
`reports/P1-WU73-e011-temporal-spectral-convergence.md`.

E005 and E009 are not invalidated and will not be rerun. E011 confirms that no
record reaches the dense, boundary-aware 90% coverage threshold, so E006-v2 is
not required. E008/E010 remain immutable historical results, while the journal
revision supersedes their exact native-grid lower-edge headlines with the
E011 convergence and window-dependence result.
