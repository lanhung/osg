# P2-WU13 gravity correction uncertainty budget

Status: implementation and unit validation complete; real component uncertainty
models and covariance groups pending data/product access.

Every gravity correction component may now carry sample-wise standard
uncertainty and a named uncertainty group. Components in the same group are
treated as fully positively correlated and their standard uncertainties are
summed before groups are combined by root-sum-square with observation
uncertainty. This avoids unjustified precision from treating outputs of one model
as independent.

If observation or any component uncertainty is absent, the result is explicitly
`incomplete`, lists every missing ID and returns no residual uncertainty. A
strict paper workflow can set `require_complete_uncertainty=True`, which rejects
that budget instead of silently replacing missing uncertainty with zero.

The correction waterfall retains each removed uncertainty series and group ID.
Real analyses must document how CMEMS, atmosphere, hydrology, elastic kernels,
calibration and drift share errors; the full-correlation grouping is a declared
conservative structure, not an inferred covariance estimate.
