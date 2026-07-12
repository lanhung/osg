# P2-WU12 non-destructive quality annotation policy

Status: implementation, frozen policy and unit validation complete; real
annotations pending SG/event data.

Candidate spikes, confirmed instrument spikes, earthquakes, maintenance, timing
issues, sensor saturation and gap-edge buffers are represented as UTC half-open
annotations with an ID, source and rationale. Applying annotations never changes,
deletes or interpolates original samples.

The frozen policy produces two masks:

- a fitting mask, which additionally removes gap-edge buffers; and
- a metric mask, which removes only confirmed contamination.

A threshold exceedance is merely `candidate_spike` and remains included until
independent evidence supports reclassification. Overlapping annotations take the
most restrictive declared action. An annotation outside the actual sample times,
an incomplete policy or duplicate annotation ID is rejected.

Any post-result policy change requires a new policy version and a full sensitivity
rerun. This prevents manual cleaning from being tuned to improve agreement with
the ocean model.
