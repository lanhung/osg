# P1-WU30 chunked spherical direct-attraction integration

Status: implemented and physics-tested

## Scope

The spherical gridded-load integrator now accepts an optional positive
`chunk_size_cells`. Gravity components, area, and mass use bounded `fsum`
buffers, followed by a deterministic sum of chunk totals. The source-grid
traversal, spherical cell area, equal-area centroid, masking, and missing-value
rules are unchanged.

## Acceptance checks

- Chunk sizes 1, 2, 3, and 7 agree with the unchunked reference to relative
  `2e-15` for a signed, irregular, antimeridian-crossing fixture.
- Included cell, masked cell, missing cell, mass, and area accounting are
  preserved.
- Repeated runs with the same chunk size are bitwise identical at the result
  object level.
- Zero, negative, non-integer, and boolean chunk sizes are rejected.
- Existing registered experiments retain their frozen output checksums.

## Limitations

This is a dependency-free bounded-buffer implementation, not yet a vectorized
or distributed production kernel. CPU, memory, and I/O scaling must be measured
before selecting a production chunk size or moving gridded convolution to the
compute plane.
