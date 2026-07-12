# P1-WU52 provisional LoadDef table adapter

Status: normalization/table plumbing implemented and unit-tested; scientific use
remains disabled.

The adapter accepts only explicit columns:

- angular distance plus an explicit `deg` or `rad` declaration;
- normalized LoadDef `gE`;
- unnormalized radial displacement in `m/kg`;
- the exact Earth radius used by the source run; and
- metadata fixed to combined elastic-gravity semantics and a reference frame.

It reverses the upstream output-header scaling
`gE_normalized = gE_SI * 1e18 * (a * theta)` after converting the supplied angle
to radians. Round-trip tests and degree/radian equivalence tests pass. The output
is a no-extrapolation combined elastic Green-function provider.

The zero-angle singular row is rejected rather than guessed. Direct attraction
does not enter this adapter and must remain the project's independent gridded
calculation. The adapter's name is deliberately `provisional`: a v1.2.2 source
checksum, tag-specific equation/sign audit, exact Earth model/reference frame,
and published benchmark are still required by the separate scientific-use gate.
