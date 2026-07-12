# P1-WU18 load Green-function interface

Status: interface implemented; physical provider integration pending

## Normalization and separation contract

Every adapter must expose a provider ID/version, Earth model, source, and one normalization: response per kilogram of source load. At each angular distance it returns three independent values:

- deformation-related gravity per source kilogram;
- gravity from elastic redistribution of internal Earth mass/potential per source kilogram;
- vertical displacement per source kilogram.

Direct Newtonian attraction is a required, explicit convolution argument computed from documented source/observer geometry. It cannot be silently included by the provider. The final total gravity sums only direct attraction, deformation gravity, and internal-mass gravity; vertical displacement is retained separately and is never added as if it were acceleration.

## Predefined acceptance checks

- A traceable analytic fixture convolves signed masses and preserves all component values and provider metadata.
- Total gravity includes exactly three gravity terms and excludes displacement.
- Zero-mass cells can be skipped safely.
- Array shape, angular range `[0, pi]`, finite inputs, nonempty provenance, and fixed normalization are validated.

## Result and limitation

All interface checks pass. No physical Earth response is claimed yet. The next gate is a mature provider (for example a reviewed SPOTL/Farrell/load-Love-number implementation) with license, version, source files, interpolation, near-field treatment, and published-case reproduction.

