# P3-WU23 Manila open source-family extraction

Status: two segment/magnitude families and the generation contract are frozen;
zero PEGS-ready numeric source scenarios are registered.

The open Zhao and Niu (2025) Scientific Data descriptor and its CC BY 4.0
Figshare dataset add a stronger source than the earlier queue. The paper divides
the Manila subduction zone into a southern 13.0--14.5 N segment and a northern
14.5--22.0 N segment. The reported 1000-year recurrence-period geodetic families
have Mw 8.1 and Mw 9.1, respectively. These are hazard-family assumptions, not
forecasts of the next earthquake.

The source domain is 119--123 E, 13--22 N and uses 1,800 Slab2.0-derived
0.1-degree subfaults (90 by 20). Longitude, latitude, depth, strike and dip are
interpolated per subfault; the PTHA adopts a constant 90-degree slip-angle/rake
assumption. The study reports 100 heterogeneous-slip realizations per
magnitude/epicentre combination and 2,015,300 potential scenarios.

This does not close the PEGS scenario contract. The released dataset contains
target-point tsunami-height/recurrence tables and wave-height/period
distributions, not a complete table of individual earthquake sources. It does
not supply per-scenario rise time, rupture velocity, mean slip, complete rupture
geometry or location-specific arrival times. Accordingly the two extracted
families remain outside `ManilaScenario`, and `scenarios` remains empty.

Sources:

- Zhao and Niu (2025), `10.1038/s41597-025-06006-4`;
- Figshare dataset `10.6084/m9.figshare.29311046.v2` (CC BY 4.0);
- Zhao and Niu (2024), `10.1029/2023JC020835`, retained for deeper source audit.
