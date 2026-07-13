# Paper 1 manuscript status

The LaTeX source is now a reproducible results draft populated from registered
experiments `P1-E005`, `P1-E006`, `P1-E008` and `P1-E009`. Engineering experiments `P1-E001` through
`P1-E004` remain excluded from scientific Results.

The abstract, Methods, Validation, Results, Discussion, Data and Code
Availability, and Limitations sections contain registered primary-branch
results. The five-figure main narrative and two versioned supplementary figures
are complete. The observable ledger prevents direct, elastic, height, total and
gradient outputs from being silently combined.

IGETS iGrav047 and author-restricted Haikou observations are supporting
published-case dependencies only. Their absence is reported as a limitation and
does not block the six-process atlas. A PEGS simulator has no Paper 1 dependency.

Remaining human-only manuscript fields are the author list, affiliations,
acknowledgements, conflicts, target journal and the final decision on whether to
include unavailable observation rows. From the repository root, rebuild every
figure, audit and the PDF with:

```bash
make paper1-release
```

The build uses frozen registered metrics; it does not download bulk data or
rerun the expensive source calculations. It records artifact checksums in
`reports/paper1_release_build.json`.
