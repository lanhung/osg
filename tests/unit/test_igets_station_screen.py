import csv
from pathlib import Path

from scripts.inventory_igets_stations import (
    build_inventory,
    parse_station_table,
)
from scripts.screen_igets_typhoon_overlap import screen

HTML = b"""
<table><tr><th>Station</th></tr>
<tr><td><a href='https://doi.org/example'>Coast</a></td><td>SG-1</td>
<td>20.0</td><td>120.0</td><td>10</td><td>2020</td><td></td><td>A</td></tr>
<tr><td>Ended</td><td>SG-2</td><td>21</td><td>121</td><td>11</td>
<td>2000</td><td>2010</td><td>B</td></tr></table>
"""


def test_parse_igets_public_station_table() -> None:
    rows = parse_station_table(HTML)
    assert len(rows) == 2
    assert rows[0]["station"] == "Coast"
    assert rows[0]["active_in_public_table"] is True
    assert rows[0]["doi_or_station_url"] == "https://doi.org/example"
    assert rows[1]["end_year"] == 2010


def test_screen_retains_only_active_nearby_typhoon(tmp_path: Path) -> None:
    inventory = build_inventory(HTML, "https://example.test", "2026-07-14T00:00:00Z")
    ibtracs = tmp_path / "ibtracs.csv"
    fields = ["SID", "SEASON", "BASIN", "NAME", "ISO_TIME", "LAT", "LON", "USA_WIND"]
    with ibtracs.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerow(
            dict(
                zip(
                    fields,
                    [
                        "2026001N",
                        "2026",
                        "WP",
                        "TEST",
                        "2026-01-01 00:00:00",
                        "20",
                        "120.5",
                        "80",
                    ],
                    strict=True,
                )
            )
        )
        writer.writerow(
            dict(
                zip(
                    fields,
                    [
                        "2026002N",
                        "2026",
                        "WP",
                        "WEAK",
                        "2026-02-01 00:00:00",
                        "20",
                        "120",
                        "40",
                    ],
                    strict=True,
                )
            )
        )
    config = {
        "station_region": {
            "minimum_latitude_deg": 0,
            "maximum_latitude_deg": 45,
            "minimum_longitude_deg_east": 100,
            "maximum_longitude_deg_east": 150,
        },
        "event_screen": {
            "required_basin": "WP",
            "minimum_season": 2023,
            "minimum_maximum_usa_wind_kt": 64,
            "maximum_closest_track_distance_km": 750,
        },
        "station_rules": {
            "require_open_ended_sensor_epoch": True,
            "deduplicate_by_station_name": True,
        },
        "interpretation": "planning only",
    }
    result = screen(inventory, ibtracs, config)
    assert result["candidate_station_count"] == 1
    assert result["stations_with_matches"] == 1
    assert result["stations"][0]["events"][0]["name"] == "TEST"
    assert result["stations"][0]["events"][0]["maximum_usa_wind_kt"] == 80
