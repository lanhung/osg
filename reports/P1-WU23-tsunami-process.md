# P1-WU23 mass-balanced propagating tsunami primitive

Status: direct-attraction long-wave reference implemented; realistic source/bathymetry and elastic coupling pending

## Source model

An equal-amplitude Gaussian sea-surface crest and trough share horizontal scale `L` and are separated along propagation. Both translate at the nondispersive shallow-water speed

```text
c = sqrt(g H).
```

Their integrated mass magnitudes are `±2 pi rho_water eta_peak L^2`; net surface-mass anomaly is zero at every time. Direct gravity is the separately integrated sum of the two translated Gaussian sheets.

## Predefined acceptance checks

- Propagation speed equals `sqrt(gH)` and quadrupling depth doubles speed.
- Analytic crest/trough masses cancel exactly.
- Crest and trough reach the observation at their expected times and produce opposite sea-level/gravity signs.
- Peak sea level and water density scale gravity linearly; reversing peak sign reverses the waveform.
- Non-positive depth, scale, separation, density, and invalid coordinates are rejected.

## Scope

This is a controlled mass-balanced wave packet, not a tsunami propagation solver. It omits earthquake/seafloor generation, dispersion, refraction, bathymetry, coastline/inundation, elastic Earth loading, and scenario-specific arrival times. Paper 3 uses published Manila tsunami scenarios for arrivals; this Paper 1 primitive only tests frequency, duration, scale, distance, and cancellation sensitivity.

