# P2-WU16 leakage-safe ocean attribution coefficient

Status: OLS attribution and held-out prediction implementation complete; event-
block uncertainty and real multi-event evaluation pending.

The fitted relation is

```text
observed - non-ocean baseline = intercept + beta * independent ocean prediction.
```

The caller supplies an event ID for every sample and a frozen set of training
events. Only included samples belonging to those events enter the fit. The model
stores the sorted training identities, fitted intercept, ocean coefficient,
coefficient standard error and residual RMSE.

The held-out prediction API rejects any event ID used during fitting. This makes
the most basic leakage error—fitting and validating on the same typhoon—an
exception rather than a reporting convention. Zero ocean-predictor variance,
unknown training events and fewer than three included samples are also rejected.

The analytic OLS standard error assumes independent residuals and is diagnostic
only. Paper-level inference still requires the preregistered event-block
bootstrap so temporal samples are not mistaken for independent events.
