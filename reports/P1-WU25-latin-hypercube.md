# P1-WU25 deterministic uncertainty sampling

Status: sampling and summary engine implemented; physical priors pending literature freeze

## Contract

Latin-hypercube sampling uses one independently jittered point in every stratum of every parameter dimension, then independently shuffles dimensions with a local seeded pseudorandom generator. Linear and logarithmic bounds are explicit. The generator does not mutate global random state.

Ensemble summaries use linearly interpolated Hyndman–Fan type-7 quantiles and preserve metric names. The Paper 1 default presentation remains median and 5–95% interval, but no physical range is accepted until its citation, definition, units, and process applicability are frozen.

## Predefined acceptance checks

- Identical seed/config gives byte-for-byte identical samples; a different seed changes them.
- Every linear and log dimension occupies every stratum exactly once.
- Known type-7 quantiles and multi-metric summaries are reproduced.
- Invalid bounds/scales, duplicate names, counts, seeds, probabilities, non-finite values, and inconsistent metric keys are rejected.

## Scope

This engine provides reproducible parameter coverage, not epistemic validity. Sampling an unsupported range more thoroughly does not make it scientifically defensible. Correlated priors, categorical model choices, Sobol sensitivity, convergence by ensemble size, and cited process-specific ranges remain required.

