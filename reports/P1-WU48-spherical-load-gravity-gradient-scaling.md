# P1-WU48 joint gravity/gradient spherical-kernel baseline

Status: current control-plane baseline captured; real-data I/O remains pending

## Run

- 90 × 180 = 16,200 cells
- simultaneous ECEF gravity vector and full 3×3 gradient tensor
- Python 3.14.4 on the inspected one-vCPU Vultr control plane
- one wall-time run per case; `tracemalloc` excludes input allocation and I/O

| Summation mode | Wall time (s) | Traced peak (bytes) | Gravity difference |
| --- | ---: | ---: | ---: |
| Unchunked | 4.342 | 7,367,264 | 0 |
| 256 cells | 4.117 | 153,800 | 0 |
| 4,096 cells | 4.186 | 1,848,344 | 0 |

The 256-cell buffer reduced traced peak allocation by about 48× for this fixture
without changing gravity. The maximum relative tensor difference was
`1.62e-16`. Timing is a single-machine engineering observation, not a
performance claim.

## Decision

The one-vCPU path remains adequate for validation subsets, not large time-varying
ocean products. CPU/RAM scaling with target dimensions and NetCDF/Zarr I/O must
be benchmarked on AutoDL before selecting production execution resources.
