# P1-WU21 translating mesoscale-eddy surface primitive

Status: surface-expression direct-attraction reference implemented; 3-D compensation and realistic priors pending

## Source model

A two-dimensional Gaussian sea-surface anomaly with scale `L` and peak `eta0` translates at constant local-x speed `v`. The characteristic passage time is `L/|v|`. At each sample, direct gravity integrates the entire Gaussian sheet to eight scale lengths using the validated off-axis surface-anomaly integrator. The reported source series is local SSH at the observation's horizontal projection.

## Predefined acceptance checks

- A central passage has local SSH and maximum vertical-gravity magnitude at passage time.
- At `t_passage ± L/|v|`, local SSH is `eta0 exp(-1/2)`.
- Central-passage vertical gravity is symmetric in time.
- A one-scale closest-approach offset reduces local peak by `exp(-1/2)` and reduces gravity peak.
- Peak SSH sign and water density scale direct gravity linearly.
- Non-positive scale/density, zero translation speed, and invalid observation coordinates are rejected.

## Scope

This model converts dynamic sea-surface height into a same-sign surface mass anomaly. It does not represent steric height, subsurface temperature/salinity density structure, geostrophic compensation, bathymetry, or elastic response. Paper 1 must compare it with compensated 3-D lens variants and must not interpret satellite SSH as barotropic mass without an ocean-bottom-pressure/density assumption.

