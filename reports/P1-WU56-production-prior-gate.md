# P1-WU56 production process-prior gate

Status: executable gate implemented; all six processes correctly blocked from
production ensembles at this stage.

The gate requires each process to have:

- at least one traceable evidence item;
- no unresolved physics or parameter fields;
- a `production_joint_design` with status `frozen`;
- explicit semantics of either `probability_prior` or
  `sensitivity_design_not_probability`; and
- frozen sample count, integer random seed, model variants and joint constraints;
- a non-empty joint parameter specification with units, linear/log scale,
  finite ordered bounds and exact evidence-parameter references; and
- for a claimed probability prior, evidence explicitly eligible for that
  probabilistic interpretation.

This distinction permits a defensible Latin-hypercube sensitivity design without
mislabeling uniform/log-uniform design measures as natural occurrence
probabilities. Named extremes cannot become distribution endpoints merely because
two numbers exist.

An empty-shell design containing only `range: [a, b]` now fails multiple explicit
blockers and cannot bypass the gate.

The current expected result is zero of six ready. Foundation experiments remain
valid engineering regressions, while a production atlas workflow must treat
`all_processes_ready=false` as a hard stop.

Run:

```bash
make audit-priors
```
