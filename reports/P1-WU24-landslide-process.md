# P1-WU24 mass-conserving submarine-landslide primitive

Status: point-mass direct gravity/gradient reference implemented; continuum slide and generated water wave pending

## Source model

Relative to the pre-event state, a transition fraction `F(t)` creates anomalies `-F M` at the solid source and `+F M` at the destination. An optional explicitly located water pair follows the same conservation rule. The transition is a half-cosine ramp with zero derivative at its start and end.

Final direct gravity and the complete gravity-gradient tensor are calculated as differences of independently validated point-source solutions. The time series scales the final change by `F(t)`.

## Predefined acceptance checks

- Net mass anomaly is exactly zero and pre/post states are exact.
- Mid-transition relocation is 50%; fraction is monotonic and endpoint increments approach zero.
- An explicit water pair adds linearly while remaining mass conserving.
- Joint translation preserves gravity and gradient.
- A far-field conserved source/destination pair decays with a dipole-like distance ratio around eight when distance doubles.
- Non-positive solid mass/duration, negative water mass, and missing water-pair coordinates are rejected.

## Scope

The point-pair model does not resolve slide geometry, acceleration history, sediment-water density contrast, bathymetric replacement, elastic deformation, seismic radiation, or generated tsunami. Those are required before realistic amplitudes are claimed. Its role is to enforce conservation, timescale sensitivity, direct-gravity/gradient signs, and far-field limits.

