# P2-WU18 event-block attribution bootstrap

Status: deterministic event-block coefficient bootstrap and validity gate
complete; real typhoon-event uncertainty remains pending data access.

Each replicate samples complete declared training events with replacement and
retains every quality-included sample in each selected event. It never resamples
individual hourly observations as though they were independent events. Training
event identities are frozen and sorted before the seeded draw.

Some block draws can contain no ocean-predictor variance. Such draws are stored
as undefined rather than silently redrawn. The result reports requested, valid,
and degenerate replicate counts, and refuses to form a confidence interval when
the preregistered minimum valid fraction is not met. Quantiles use a documented
linear interpolation over valid coefficients.

This supplies the uncertainty mechanism needed for the positive attribution-
coefficient gate. It does not replace time-series residual diagnostics or prove
cross-event generalization without real held-out events.
