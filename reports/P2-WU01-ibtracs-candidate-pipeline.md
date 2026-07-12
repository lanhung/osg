# P2-WU01 IBTrACS candidate-event pipeline

Status: retrieval and selection pipeline prepared; dataset download pending network

## Frozen source

The source is NOAA NCEI IBTrACS v04r01, `last3years` CSV, dataset DOI
`10.25921/82ty-9e16`. The official file is updated several times per week under
the same filename, so the downloader records retrieval time, final URL, HTTP
Last-Modified, byte count, and SHA-256.

The source and open-use/citation requirements are recorded in
`data/manifests/paper2_ibtracs.json`.

## Candidate rule

The first-pass regional filter retains Western Pacific (`WP`) tracks with at
least one reported position inside 5–25°N, 100–125°E. It reports only the
regional time/coordinate envelope and keeps WMO and USA wind/pressure fields
separate; it does not homogenize unlike averaging periods or agencies.

Passing this filter means only “entered the broad South China Sea study box.” It
does not establish SG coverage, surge magnitude, data completeness, or final
event suitability.

## Commands after network restoration

```bash
python3 scripts/fetch_ibtracs.py \
  --manifest data/manifests/paper2_ibtracs.json \
  --output data/raw/paper2/ibtracs.last3years.list.v04r01.csv

python3 scripts/select_ibtracs_candidates.py \
  --input data/raw/paper2/ibtracs.last3years.list.v04r01.csv \
  --config configs/paper2/ibtracs_south_china_sea.json \
  --output data/interim/paper2/ibtracs_south_china_sea_candidates.json
```

## Next gate

Intersect candidate windows with verified SG gravity/pressure/log coverage, then
freeze ±7-day windows before inspecting gravity residuals.
