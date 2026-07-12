# P1-WU17 instrument noise-curve schema

Status: implemented; awaiting independent human review

## Contract

Every curve records instrument ID, observable, ASD unit, positive increasing frequency nodes, positive one-sided ASD values, source, curve version, and relative digitization uncertainty. Interpolation is log-log, suitable for locally power-law spectra. Extrapolation is forbidden.

PSD is produced only by explicitly squaring ASD, preventing amplitude/power unit confusion. Curves for vertical gravity, gravity gradient, acceleration, strain-equivalent environmental channels, or other observables remain separate and cannot be merged merely because their plots share a frequency axis.

## Predefined acceptance checks

- Original nodes are exact.
- A geometric frequency midpoint returns the geometric ASD midpoint for a power-law interval.
- PSD equals ASD squared.
- Both low- and high-frequency extrapolation are rejected.
- Metadata, array length/order, positivity, finite values, and digitization uncertainty are validated.

## Result

All checks pass. No real instrument curve is asserted by this work unit. Each real curve still requires authoritative source review, extraction method, units, operating conditions, response correction, uncertainty, and versioned data points.

