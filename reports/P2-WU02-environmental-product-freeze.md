# P2-WU02 ERA5 and CMEMS product-role freeze

Status: catalogue products and physics roles frozen; authenticated retrieval pending

## Products

- ERA5 hourly single levels: `reanalysis-era5-single-levels`, DOI
  `10.24381/cds.adbb2d47`, 0.25° atmospheric grid, hourly.
- Copernicus Marine global ocean physics analysis/forecast:
  `GLOBAL_ANALYSISFORECAST_PHY_001_024`, hourly sea-level dataset
  `cmems_mod_glo_phy_anfc_merged-sl_PT1H-i`, DOI `10.48670/moi-00016`.

The default broad extraction box is 5–30°N, 100–130°E with event windows of
seven days on either side. Exact windows are generated only after IBTrACS and SG
coverage are intersected.

## Physical-role gate

ERA5 surface pressure is the atmospheric column-load input. Mean-sea-level
pressure and winds are event diagnostics. Precipitation is hydrology forcing.
Significant wave height is only a sea-state/microseism auxiliary and is never
converted into an extra water mass.

CMEMS sea level is the candidate ocean surface-load input, but its variable
metadata and treatment of tides, inverse-barometer response, and mean dynamic
topography must be inspected with the installed Copernicus Marine client before
download. Until then the atmosphere–ocean double-count gate remains unresolved.

## Access state

ERA5 requires a CDS account and accepted CC-BY terms. Copernicus Marine dataset
metadata and data retrieval require the client/network path. No credentials are
stored in Git, and no product is yet marked downloaded.
