# P1-WU70 Structural-variant closure

Date: 2026-07-12

Registered experiment `P1-E007-structural-variant-closure` passes. It closes
every structural branch left pending by `P1-E006` through either an
evidence-supported implementation or a disclosed scientific exclusion. None of
the decisions depends on IGETS, Haikou authorization, or PEGS.

The implemented branch maps the Tang et al. (2012) propagated Tohoku energy of
3.0 PJ (6% relative uncertainty) to the mass-balanced Gaussian crest--trough
packet under the explicit linear-long-wave convention
`E = rho*g*integral(eta^2 dA)`. Across registered 300--400 km separations, the
central idealized crest amplitude is 4.359 m; energy uncertainty maps to
4.226--4.488 m. This is reported separately from the 1.0--1.8 m deep-ocean
amplitude-normalized branch and is not a probability interval.

The other branches are excluded rather than assigned surrogate values:

- the eddy profile design cannot simultaneously fix peak SSH, speed-based
  radius, and positive mass across Gaussian and compact quadratic profiles;
- a compensated eddy needs a supported SSH-to-density-profile mapping;
- continuous mode-1 and free-surface internal-wave branches need a vertical
  density profile/eigenfunction and a coupling coefficient;
- Mediterranean/Storfjorden slide evidence does not close volume and duration
  jointly; and
- the generated-water-wave slide branch needs an event-specific generation or
  entrainment transfer model.

The registered output SHA-256 is
`589f8266eb45518f9edc6df1ccfdc1a6fdd8019b0c98b65a220cbb38ce61ae78`.
The gate is a model-form disposition, not evidence that excluded branches are
physically negligible.

The updated eight-page manuscript builds without unresolved references or
citations and has SHA-256
`4aca86e67b04d8f0be3335575b3c2bbff8207cc3544f7df6af03278a4891da00`.
The repository audit passes 461 tests and 12 subtests.
