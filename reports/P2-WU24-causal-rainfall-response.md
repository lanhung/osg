# P2-WU24 causal two-timescale rainfall response

Status: generic causal two-reservoir response, gravity-ledger adapter, uncertainty
propagation and physics tests complete; mixture weight, real forcing, catchment
geometry and elastic response pending.

Each precipitation value is an interval accumulation assigned at its timestamp.
Stored water decays exactly over the actual elapsed interval before the new
increment enters the fast and slow reservoirs. The effective height is an
explicit convex mixture, so the same rainfall increment is not counted twice.
Missing values and negative precipitation are rejected rather than interpolated.

The Haikou VOR method contract supports time constants of 1 hour and 720 hours,
which are recorded in `configs/paper2/hydrology_response.json`. The available
evidence does not freeze the mixture weight, so the production configuration
leaves it null and requires either equation-level evidence or training-event-only
estimation with held-out sensitivity.

The adapter maps equivalent water height into a `GravityCorrectionComponent`
with the effect ID `land_hydrology_direct_local_slab` and propagates height
standard uncertainty through the analytic slab factor. This remains a baseline,
not a complete typhoon-season hydrology correction.
