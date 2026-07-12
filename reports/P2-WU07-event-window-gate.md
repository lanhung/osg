# P2-WU07 event-window and data-gate contract

Status: implemented; real event table pending SG coverage

## Raw-data gate

The audit implements the predeclared alternatives exactly: at least one station
with three typhoon windows, or at least two stations with two typhoon windows
each. An event may cover multiple stations and contributes once to each.

## Evaluation gate

Paper-level readiness additionally requires at least one completely held-out
typhoon, one non-typhoon strong-weather control, three quiet windows, and no
overlap at a shared station across event/split records. These conditions prevent
near-identical samples from leaking between fit and evaluation sets.

All timestamps must be explicit UTC. Event type, split role, stations and source
are mandatory. The versioned real-event manifest remains empty until IBTrACS is
intersected with verified SG gravity/pressure/log coverage; therefore no data
Go decision is currently claimed.
