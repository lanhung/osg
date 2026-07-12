# P2-WU28 CMEMS pressure-response semantics

Status: inverse-barometer ownership closed; event inputs remain unavailable.

The frozen product is Copernicus Marine
`GLOBAL_ANALYSISFORECAST_PHY_001_024`, dataset
`cmems_mod_glo_phy_anfc_merged-sl_PT1H-i` (MOWL), DOI
`10.48670/moi-00016`. The Product User Manual and Quality Information
Document were reviewed on 2026-07-12.

MOWL exposes the relevant sea-level contributions separately. Its
`sea_surface_height` variable is explicitly defined as ocean dynamic sea level
without tides and surface-pressure forcing. `invert_barometer` is calculated
from IFS atmospheric pressure; `ocean_tide` and `tide_loading` are separate;
and `total_sea_level` combines the dynamic, tide, inverse-barometer, global
steric and global mass-volume terms (with the documented exception that load
tide is not in the total).

Paper 2 therefore freezes `sea_surface_height` as the ocean input and excludes
the MOWL `invert_barometer` component. The separately implemented ERA5
equilibrium inverse-barometer response is the sole owner of
`ocean_inverse_barometer_response`. This closes the composition ledger without
claiming that MOWL and ERA5 pressure fields are interchangeable.

This audit removes a method-level ambiguity only. CMEMS retrieval, anomaly
reference construction, station-specific coverage, SG observations and event
attribution remain pending. Every event manifest must record the exact selected
variable so that `total_sea_level` cannot silently replace it.

Primary documentation:

- `https://documentation.marine.copernicus.eu/PUM/CMEMS-GLO-PUM-001-024.pdf`
- `https://documentation.marine.copernicus.eu/QUID/CMEMS-GLO-QUID-001-024.pdf`
- `https://data.marine.copernicus.eu/product/GLOBAL_ANALYSISFORECAST_PHY_001_024/description`
