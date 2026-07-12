# P1-WU37 evidence-aware parameter design

Status: implemented and unit-tested

## Problem prevented

A Latin-hypercube over convenient minimum/maximum values is not automatically a
Monte Carlo uncertainty distribution. Reporting its 5th–95th percentiles as
probabilities would overstate engineering fixtures or broad scenario ranges.

## Contract

Every varied parameter now records unit, bounds, linear/log scale, evidence
status, range semantics, and sources. Engineering fixtures cannot be labelled
probability priors. Literature- or data-supported ranges require source records.

The sampler propagates one of two explicit interpretations:

- `space_filling_scenario_design_not_probability_samples`; or
- `probability_prior_samples`, only when every dimension is explicitly a
  supported probability prior.

## Next use

The six process manifests will first be encoded as scenario envelopes. A range
will be upgraded to a probability prior only when the cited source or empirical
dataset actually supports a distribution, not merely representative extrema.
