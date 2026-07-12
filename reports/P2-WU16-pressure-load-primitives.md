# P2-WU16 pressure-load primitives

Status: hydrostatic column conversion and mass-conserving inverse-barometer
reference implementation complete; production atmospheric attraction, elastic
loading, regional boundary validation, and real ERA5/CMEMS fields pending.

Surface-pressure anomaly is converted to equivalent atmospheric column surface
density with `delta_sigma = delta_p / g`. This identity is retained as an input
primitive and is not presented as a complete atmospheric direct-attraction model,
because the vertical density distribution still matters near a gravimeter.

The equilibrium inverse-barometer response uses
`eta = -(delta_p - mean_ocean_delta_p)/(rho_w g)`. The pressure mean is weighted
by effective ocean-cell area, including partial cells. The output records the
reference pressure, included area, and net water-mass anomaly. Tests require the
closed-domain mass anomaly to vanish to floating-point precision and verify that
low pressure raises sea level.

Atmospheric column mass and ocean inverse-barometer response remain separate
effects in the gravity budget. Product metadata must establish whether a CMEMS
field already includes pressure-driven response before either is subtracted from
observations.
