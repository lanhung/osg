# P1-WU09 density-compensation and dipole suppression

Status: implemented; awaiting independent human review  
Model: two identical 3-D Gaussian density grids with opposite signs, vertically separated by two scale lengths

## Scientific purpose

An internal wave or compensated eddy cannot be estimated by converting an affected water volume into a same-sign surface load. Equal positive and negative density anomalies remove the net-mass (monopole) term. Their far field is then controlled by the spatial separation of the anomalies and decays approximately as a dipole.

## Predefined checks

- Discrete signed mass sums to zero within numerical tolerance.
- When observation distance doubles from 20 to 40 scale lengths, the uncompensated Gaussian acceleration ratio remains consistent with `r^-2` (accepted interval 3.0–5.5).
- The compensated-pair ratio is consistent with faster dipole-like decay (accepted interval 6.0–11.0 around the ideal `r^-3` ratio of 8).
- At 20 scale lengths, compensation suppresses vertical gravity below 20% of the positive Gaussian alone.

## Result

All checks pass. The frozen calculation produced:

| Metric | Result |
| --- | ---: |
| Discrete net mass | `0.000e+00 kg` |
| Compensated acceleration at `20 L` | `-2.622e-10 m s^-2` |
| Compensated acceleration ratio, `20 L / 40 L` | `8.030` |
| Uncompensated acceleration ratio, `20 L / 40 L` | `4.213` |
| Compensated/uncompensated magnitude at `20 L` | `0.1814` |

This is a qualitative/limiting physics gate, not yet a realistic ocean stratification model. Paper 1 must propagate density profile, interface displacement, vertical separation, and source geometry uncertainty instead of representing internal waves as uncompensated sea-level mass.
