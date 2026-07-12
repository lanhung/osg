# P3-WU02 Manila source-scenario and tsunami-arrival contract

Status: validation contract implemented; no numeric literature scenario registered

## Contract

Every earthquake scenario requires segment, Mw, strike/dip/rake, top depth,
rupture dimensions, mean slip, rise time, rupture velocity and source. Every
tsunami arrival is nested under that scenario and carries a location ID,
arrival-definition text, numeric time and source.

This prevents a Hong Kong arrival from being reused for Hainan, or one rupture
segment's arrival from being attached to another source.

## Evidence state

The 2023 Chinese article landing page timed out in the current retrieval path,
so its tables have not been transcribed. The Hong Kong Observatory's “more than
about three hours” statement is retained only as qualitative context. It is not
converted into an exact `10,800 s` benchmark. The 2024 JGR Oceans maximum-event
study is queued for full parameter audit.

Accordingly, the versioned manifest contains zero scientific scenarios. Unit
tests use a conspicuously labelled nonphysical fixture only.

## Next gate

Acquire full texts/tables, record page-level provenance and modeling assumptions,
then register multiple segment-specific scenarios and location-specific arrival
distributions. Only those frozen records may feed PEGS simulations.
