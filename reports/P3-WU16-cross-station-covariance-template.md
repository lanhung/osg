# P3-WU16 cross-station covariance template baseline

Status: positive-definite cross-station covariance reference complete; temporal
colour, nonstationarity and real calibration windows remain unavailable.

The scorer evaluates the network matched statistic using a frozen station
covariance matrix and Cholesky solves rather than an explicit inverse. Covariance
station order, source ID and calibration quiet-window IDs are mandatory. The
matrix must be finite, symmetric and positive definite.

Physics tests prove that a diagonal covariance reproduces the existing
independent-noise score and that strong positive common noise reduces the
apparent gain of equal coherent stations. Masks still discard whole network
windows without temporal compaction.

This closes only the instantaneous cross-station correlation gap. Real PEGS
analysis must estimate covariance on non-event calibration data, test seasonal
and typhoon strata, account for temporally coloured noise or whitened residuals,
and calibrate operational thresholds on held-out continuous streams.
