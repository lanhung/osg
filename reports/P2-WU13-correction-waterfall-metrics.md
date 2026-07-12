# P2-WU13 gravity-correction waterfall metrics

Status: implementation and unit validation complete; real waterfall pending SG
and component data.

Each correction stage now preserves not only its input, removed series and output,
but also the component source and physical-effect IDs. The summary reports:

- input, removed and output means;
- input, removed and output RMS;
- peak absolute removed amplitude;
- stage and total RMS change fractions; and
- final sample-wise closure error.

RMS change is descriptive, not automatically an improvement: a physically
required correction can increase residual RMS, and such a negative fraction is
retained. If the input RMS is zero, the fractional change is explicitly `None`
rather than divided by an epsilon. The summary reads the immutable correction
chain and does not modify any series.
