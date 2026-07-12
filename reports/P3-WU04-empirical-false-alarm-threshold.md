# P3-WU04 empirical false-alarm threshold

Status: implemented and unit-tested

## Method

Noise scores are converted to operational false alarms per 30-day month using
the declared sliding-window step. The algorithm selects the lowest observed
threshold whose empirical exceedance rate does not exceed the target. Score ties
are handled conservatively.

If the noise record is too short to resolve one exceedance at the requested
rate, the threshold is placed immediately above the maximum observed score and
the observed count is zero. The result reports the minimum nonzero FAR that the
record length could resolve.

## Consequence

“At most one false alarm per month” cannot be validated with a handful of quiet
windows, particularly for strongly overlapping second-scale windows. Papers 2
and 3 must either collect enough continuous empirical noise, reduce independent
decision cadence with justification, or state that only a zero-exceedance upper
constraint was observed. Gaussian-tail extrapolation is a separate model and
cannot replace this empirical calibration silently.

Held-out detection probability is computed only after the threshold is frozen.
