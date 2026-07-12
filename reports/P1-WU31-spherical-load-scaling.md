# P1-WU31 spherical-load kernel scaling baseline

Status: control-plane baseline captured; production I/O benchmark pending

## Frozen run

- Grid: 90 × 180 = 16,200 spherical cells
- Python: 3.14.4
- Measurement: one wall-time run per case and `tracemalloc` peak attributable
  to the integration call
- Excluded: input-grid allocation, dataset decoding, disk/network I/O, and
  process-wide native allocations

## Results

| Summation mode | Wall time (s) | Traced peak (bytes) | Relative gravity difference |
| --- | ---: | ---: | ---: |
| Unchunked | 2.210 | 2,633,944 | 0 |
| 256 cells | 1.928 | 58,080 | 0 |
| 4,096 cells | 2.018 | 663,304 | 0 |

At this size the 256-cell buffer reduced traced kernel peak allocation by about
45× with no numerical change in this fixture. Single-run timing differences are
not treated as performance claims.

## Decision

The dependency-free CPU path is adequate for validation fixtures and compact
regional subsets. A production decision still requires repeated scaling runs,
real NetCDF/Zarr decoding and I/O, and the actual target grid/time dimensions.
The current evidence does not justify moving Paper 1 or Paper 2 to GPU.

## Re-run

```bash
python3 scripts/benchmark_spherical_load.py \
  --latitude-cells 90 --longitude-cells 180 \
  --chunk-sizes 256 4096 --output /tmp/P1-WU31.json
```
