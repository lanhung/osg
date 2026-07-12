# P1-WU20 storm-surge/typhoon-setup process primitive

Status: direct-attraction transient reference implemented; elastic response and event priors pending

## Source model

Sea-level setup/setdown is a finite uniform disk with a smooth asymmetric Gaussian time envelope. Separate rise and fall scales allow rapid storm forcing followed by slower relaxation without introducing a derivative jump at peak time. The time integral is

```text
A sqrt(pi/2) (tau_rise + tau_fall).
```

## Predefined acceptance checks

- Peak gravity equals peak sea level times the independent one-metre disk response.
- Values one rise/fall scale from the peak equal `A exp(-1/2)` independently.
- The finite sampled event integral agrees with the analytic infinite-window integral within `1e-5` for the frozen wide window.
- A transient occupies multiple spectral bins rather than masquerading as a periodic line.
- Source sign, amplitude, and density scale direct gravity linearly.
- Non-positive event scales and water density are rejected.

## Scope

This is not a hydrodynamic typhoon model. It does not infer sea level from wind/pressure, resolve coastlines or bathymetry, include inverted-barometer dynamics, or add elastic Earth response. Paper 2 will use observed/modelled sea-level fields rather than fit this shape as truth; Paper 1 uses it only for controlled frequency/duration/distance sensitivity.

