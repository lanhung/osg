# P1-WU32 timebase and gap policy

Status: implemented and unit-tested

## Frozen convention

Before spectral analysis, timestamps must be finite and strictly increasing and
the expected cadence must be declared. Missing/non-finite samples and cadence
violations split the record into finite uniform segments. Short runs are counted
and excluded. No interpolation, cadence conversion, or sample synthesis occurs.

The default cadence tolerance is relative `1e-6`; callers must override it
explicitly when instrument timing evidence warrants another value. Any later
resampling must be a separate operation with a documented anti-alias filter.

## Acceptance checks

- Missing values and irregular intervals create the expected segment boundaries.
- Retained, missing, and short-run counts close exactly to input length.
- Cadence tolerance changes are observable and tested.
- Duplicate/non-finite timestamps and invalid configuration are rejected.
- Segment samples are exact subsets of input samples.

## Limitation

This module defines the safe no-resampling baseline. Clock corrections, leap
seconds, drift estimation, anti-alias filtering, and uncertainty propagation
remain instrument- and dataset-specific work for Papers 2 and 3.
