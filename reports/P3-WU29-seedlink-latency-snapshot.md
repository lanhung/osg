# P3-WU29 SeedLink latency snapshot

Status: endpoint and three current streams demonstrated once; operational
latency remains unresolved.

A frozen 30-minute query used `rtserve.earthscope.org:18000`, the current
EarthScope SeedLink endpoint. At the common query end, HK.HKPS, IU.DAV and
MY.KKM returned LHZ packets with observed latest-packet ages of 720.10, 94.10
and 228.10 seconds. IC.QIZ and TW.KMNB produced client query errors rather than
auditable packets; these are not reclassified as offline stations.

This is one packet-recency snapshot, not an uptime or latency distribution.
EarthScope exposes open streams that it receives in real time but does not
guarantee continuity or quality. Therefore no station is yet marked
operationally suitable. A longitudinal monitor, outage accounting, clock checks
and an explicit service-level decision threshold are still required before an
early-warning claim.
