# P2-WU29 IGETS–IBTrACS acquisition-priority screen

Status: public inventory and acquisition-priority screen complete; authenticated
file coverage and every scientific evidence gate remain pending.

The official IGETS public table was fetched and parsed on AutoDL on 2026-07-14.
It contains 49 station names, 69 sensor epochs and 39 sensor epochs without a
listed end year. The public table states that Level 1 contains raw gravity and
local pressure at 1--2 s and one-minute cadence, but its station epochs are not
proof that any particular event-year file is downloadable.

The screen retained public-table-active stations in 0--45 degrees N and
100--150 degrees E and compared them to WP IBTrACS tracks from 2023 onward. A
track was retained for data-inquiry priority when its maximum USA wind anywhere
on the track was at least 64 kt and one track point was within 750 km of the
station. This is deliberately a broad acquisition screen: intensity at closest
approach, local ocean response, station operation and SG file coverage are not
asserted.

| Public-table station | Active sensor | Inquiry matches | Strong 2023--2024 examples |
| --- | --- | ---: | --- |
| Hsinchu | GWR T048 | 23 | Gaemi 24.6 km; Kong-rey 102.0 km; Haikui 211.3 km; Doksuri 230.7 km |
| Matsushiro | GWR T011 TT70 | 15 | Shanshan 179.5 km; Kong-rey 193.3 km; Lan 307.5 km |
| Mizusawa | GWR T007 TT70 | 14 | Maria 29.8 km; Ampil 371.9 km; Lan 431.8 km |
| Wuhan | OSG 065 | 8 | Doksuri 95.8 km; Gaemi 108.5 km; Bebinca 255.7 km |
| Lijiang | OSG 066 | 3 | Talim 496.4 km; Yagi 557.0 km |

Hsinchu is therefore the first authenticated-directory inquiry, followed by
Matsushiro/Mizusawa and Wuhan. This ordering is not final station selection.
Wuhan's hydrological closure may be harder despite close decaying-storm tracks;
Japanese stations may have stronger seismic and coastal-ocean complications;
and Hsinchu still requires local pressure, calibration, jump/maintenance and
redistribution terms. Actual remote file coverage may reverse the order.

The next authorized action is a header-first authenticated inventory:

1. list Hsinchu, Matsushiro, Mizusawa and Wuhan Level 1 directories and exact
   available years;
2. retrieve only documentation, calibration and representative headers;
3. verify gravity and pressure channels, cadence, units, sign, time standard,
   scale factor and pre-applied corrections;
4. freeze event/control windows from actual file coverage before bulk download
   or inspection of gravity amplitudes.

AutoDL independently resolved `igetsftp.gfz.de` and reached TCP port 22 on
2026-07-14. This demonstrates network reachability only, not authentication or
server identity; the PI must verify the host key during the first interactive
login.

Reproduction commands are:

```bash
python scripts/inventory_igets_stations.py \
  --retrieved-utc 2026-07-14T00:00:00Z \
  --output data/manifests/igets_public_station_inventory_2026-07-14.json

python scripts/screen_igets_typhoon_overlap.py \
  --station-inventory data/manifests/igets_public_station_inventory_2026-07-14.json \
  --ibtracs data/raw/paper2/ibtracs.last3years.list.v04r01.csv \
  --config configs/paper2/igets_typhoon_station_screen.json \
  --output reports/paper2_igets_typhoon_screen_2026-07-14.json
```

Output SHA-256 values:

- public inventory: `14fbeaf3b30db007bbe5db26c5fc4bc407012b08df681c6dab2d64376f2d1578`;
- station/event screen: `adecc01b330382694f7f3fdca249ffa3e5be0a17ad16973c7807677c920344b0`.

Neither output authorizes typhoon attribution, station selection, bulk download,
or a Paper 2 result claim.
