# P2-WU23 local hydrology slab baseline

Status: groundwater-to-equivalent-water and infinite-slab direct-attraction
baselines complete; real rainfall/groundwater data, lag model, finite domain and
elastic response pending.

Groundwater-level change is converted to equivalent water height using an
explicit effective porosity. The gravity baseline then applies the infinite
Bouguer-slab magnitude `2*pi*G*rho_w*h`. Under the repository's local-up-positive
convention, added water below the sensor produces negative vertical gravity.

Physics tests freeze linearity, sign reversal for a hypothetical load above the
sensor, and the reference magnitude of about 0.04193586 microgal per millimetre of
water. The approximation is intentionally simple: it is a transparent sensitivity
branch and cannot stand in for catchment geometry, vadose-zone dynamics, delayed
rainfall response, or elastic Earth loading.
