# P1-WU19 periodic tide process primitive

Status: direct-attraction reference implemented; elastic response and realistic harmonic priors pending

## Source model

A uniform finite disk has sea-level anomaly

```text
eta(t) = A cos(2 pi t / P + phase)
```

and signed surface density `rho_water eta(t)`. Its on-axis vertical gravity is obtained by scaling the independently validated analytic disk solution. The record uses an endpoint-exclusive regular time axis.

## Predefined acceptance checks

- Peak gravity equals peak sea level times the independent one-metre disk response.
- Two complete cycles have negligible mean and repeat sample-for-sample within floating-point tolerance.
- The direct DFT has its dominant positive-frequency bin at `1/P`.
- Gravity scales linearly with sea-level amplitude and water density.
- Phase shifts source and gravity together; invalid period, density, and time order are rejected.

## Scope

This is a controlled atlas primitive, not a global tide model. It excludes coastline geometry, multiple tidal constituents, self-attraction/loading feedback, elastic deformation, ocean-bottom pressure dynamics, station height/topography, and empirical instrument/environment noise. Paper 1 completion requires those limitations to appear explicitly and realistic priors to be cited.

