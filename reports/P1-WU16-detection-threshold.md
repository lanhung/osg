# P1-WU16 Paper 1 reference detection threshold

Status: implemented; awaiting independent human review  
Scope: uniform atlas comparison, not operational alerting

## Frozen reference

The normalized matched-filter statistic is assumed standard normal under the null and unit-variance normal with mean equal to expected SNR under a perfectly known signal. Tests are one-sided. For multiple independent trials, the per-trial probability is selected so that

```text
P(at least one false alarm) = family_false_alarm_probability
```

exactly, rather than using an undocumented “SNR > 5” rule.

The baseline Paper 1 illustrative convention is:

| Quantity | Value |
| --- | ---: |
| Family false-alarm probability | `0.001` |
| Independent trials | `1` |
| Statistic threshold | `3.0902323` |
| Target detection probability | `0.90` |
| Required expected SNR | `4.3717838717` |

Every atlas result must show sensitivity to observation time, PSD, trials count, and threshold convention.

## Predefined acceptance checks

- Known one-sided 5% and 0.1% normal quantiles are reproduced.
- More trials increase the family-wise threshold.
- Required-SNR inversion returns the target detection probability.
- Expected SNR equal to threshold gives 50% detection.
- Invalid probabilities, trials, and negative expected SNR are rejected.

## Limitation

Papers 2 and 3 cannot use this Gaussian reference as their false-alarm evidence. They require empirical quiet-window or continuous-stream false triggers per month/year under nonstationary, correlated, typhoon/microseism, gap, and outage conditions.
