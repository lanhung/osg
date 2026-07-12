# P3-WU03 PEGS warning-time metric contract

Status: implemented and unit-tested

## Frozen signs and times

All times are seconds after origin. The timeline stores P trigger, PEGS
detection, PEGS reliable magnitude, conventional reliable magnitude, and a set
of location-specific tsunami arrivals.

```text
characterization_gain = conventional_reliable_Mw - PEGS_reliable_Mw
PEGS_vs_P = PEGS_detect - P_trigger
lead(location) = tsunami_arrival(location) - PEGS_reliable_Mw
```

Positive characterization gain means PEGS is earlier. Negative gain is retained
as a negative result, not relabelled. Negative `PEGS_vs_P` means PEGS detection
precedes the chosen P trigger. Lead time is never computed from a universal
arrival constant.

## Validation

Reliable PEGS magnitude cannot precede PEGS detection. Arrival locations must be
unique and nonempty. Numeric times must be finite and non-negative/positive as
appropriate. The contract deliberately does not assume PEGS must beat P waves or
conventional magnitude estimation; those are experiment outcomes.
