# P2-WU20 paired held-out model improvement

Status: mask-identical baseline/candidate comparison and strict decision gate
complete; held-out typhoon results pending data access.

The comparison evaluates the baseline model and the candidate model containing
the independently predicted ocean term on the same timestamps and the same
frozen quality mask. Positive RMSE improvement means lower candidate RMSE;
positive explained-variance improvement means higher candidate explained
variance. The fractional RMSE improvement is undefined when baseline RMSE is
zero rather than divided by an arbitrary epsilon.

The strict preregistered gate passes only when both RMSE and explained variance
improve by a value strictly greater than zero. Constant observations have no
defined explained variance and therefore cannot pass. This API supplies the
numeric decision rule but does not assert success until it is run on a typhoon
that was excluded from all parameter fitting.
