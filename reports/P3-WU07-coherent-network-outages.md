# P3-WU07 coherent network and station-outage baseline

Status: implemented and unit-tested

## Coherent baseline

Already time/phase-aligned station series are combined with explicit station
weights normalized by their L2 norm. Four identical unit-noise-normalized
coherent stations therefore produce the expected `sqrt(4)` signal gain. Signed
weights permit physically predicted polarity; station identities must match the
weight map exactly.

Alignment, response removal and per-station noise normalization are deliberately
outside this function and must be validated before stacking real data.

## Outage experiments

Deterministic seeded masks remove a fixed rounded station count for each declared
fraction. This directly supports 0%, 20% and 40% outage ablations while retaining
the exact available station IDs for every trial. At least one station must remain.

The physical coherent stack is the interpretable baseline that any later GNN
must outperform on fully held-out rupture segments and noise dates.
