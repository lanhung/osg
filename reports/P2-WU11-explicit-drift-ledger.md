# P2-WU11 explicit SG drift correction

Status: implementation and unit validation complete; real drift model pending
instrument history and quiet/pre-event data.

The correction accepts only a declared model with an ID, UTC reference and
validity interval, linear/quadratic rates and standard uncertainties, source,
rationale, and fit-data role. Allowed fit roles exclude the target event window.

The full removed drift and propagated uncertainty are retained sample by sample.
The implementation preserves the sign before and after the reference epoch,
requires strictly increasing UTC samples, and refuses extrapolation at or beyond
the validity end. It does not estimate a drift model.

This prevents a flexible trend fitted over a typhoon window from absorbing the
slow ocean-loading signal that Paper 2 aims to attribute. Real model selection
must be frozen from external calibration, pre-event data, quiet controls, or
long-term instrument history and tested as a sensitivity branch.
