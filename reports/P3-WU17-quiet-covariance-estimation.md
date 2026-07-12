# P3-WU17 quiet-window covariance estimation

Status: complete-case quiet covariance estimator with explicit shrinkage complete;
real noise windows and stratum-specific adequacy checks remain unavailable.

The estimator accepts only windows explicitly labelled by caller-supplied quiet
IDs and records those IDs in the covariance model. It uses samples where every
network station passes its original mask, mean-centres each station, and computes
the unbiased sample covariance. Masked samples are not compacted within a station.

An explicit diagonal-shrinkage coefficient multiplies off-diagonal terms by
`1-lambda`; no hidden ridge epsilon is added. The coefficient, complete sample
count, method and source ID are saved. The resulting matrix must still pass the
symmetric positive-definite Cholesky gate.

Production analysis must freeze shrinkage using training/calibration data only,
run sensitivity across calm, seasonal, microseism and typhoon strata, and keep
all held-out event and false-alarm streams outside covariance estimation.
