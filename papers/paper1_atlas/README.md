# Paper 1 manuscript status

The LaTeX source is now a reproducible results draft populated from registered
experiments `P1-E005` and `P1-E006`. Engineering experiments `P1-E001` through
`P1-E004` remain excluded from scientific Results.

The abstract, Methods, Validation, Results, Discussion, Data and Code
Availability, and Limitations sections contain registered primary-branch
results. Frequency coverage and the process--instrument coverage matrix are
complete. Distance-amplitude and sensitivity figures are complete for the
primary model branches but remain subject to structural-variant closure listed
in `P1-E006`.

IGETS iGrav047 and author-restricted Haikou observations are supporting
published-case dependencies only. Their absence is reported as a limitation and
does not block the six-process atlas. A PEGS simulator has no Paper 1 dependency.

Remaining human-only manuscript fields are the author list, affiliations,
acknowledgements, conflicts, target journal and the final decision on whether to
include unavailable observation rows. Build with:

```bash
cd papers/paper1_atlas
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```
