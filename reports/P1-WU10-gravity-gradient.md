# P1-WU10 gravity-gradient tensor validation

Status: implemented; awaiting independent human review  
Convention: `T_ij = partial g_i / partial x_observation_j`  
Units: `s^-2`

## Model

For displacement `d = x_source - x_observation`,

```text
T_ij = G m [3 d_i d_j / r^5 - delta_ij / r^3].
```

Rows identify acceleration components and columns identify observation-coordinate derivatives. The tensor is summed cell-by-cell for discretized signed volume-density anomalies using deterministic component-wise `math.fsum`.

## Predefined acceptance checks

- On a coordinate axis, eigenvalues are `(-1, -1, 2) Gm/r^3`.
- The tensor is symmetric and trace-free outside a source.
- Every component agrees with central finite differences of the independently implemented acceleration vector within relative `1e-6`.
- Doubling distance reduces tensor magnitude by eight.
- Negative source mass reverses every component.
- The volume-cell tensor equals the deterministic sum of individual point tensors.
- Zero mass is zero away from the source and coincident geometry is rejected.

## Result

All checks pass. This work unit fixes the gradient convention required by Paper 1. Instrument-specific gradiometer axes, transfer functions, and noise units remain part of the instrument-model phase.

