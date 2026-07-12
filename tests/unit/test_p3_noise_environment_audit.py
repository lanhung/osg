from datetime import UTC, datetime

from scripts.audit_p3_noise_environment import (
    event_station_candidate,
    haversine_km,
    interval_overlaps,
)

UTC = UTC


def test_haversine_zero_and_quarter_circumference() -> None:
    assert haversine_km(10.0, 20.0, 10.0, 20.0) == 0.0
    assert abs(haversine_km(0.0, 0.0, 0.0, 90.0) - 10007.557) < 0.01


def test_closed_interval_overlap() -> None:
    start = datetime(2024, 1, 1, tzinfo=UTC)
    end = datetime(2024, 1, 2, tzinfo=UTC)
    assert interval_overlaps(start, end, end, datetime(2024, 1, 3, tzinfo=UTC))
    assert not interval_overlaps(
        start, end, datetime(2024, 1, 3, tzinfo=UTC), datetime(2024, 1, 4, tzinfo=UTC)
    )


def test_candidate_requires_magnitude_distance_and_arrival_overlap() -> None:
    rules = {
        "global_minimum_magnitude": 6.0,
        "regional_minimum_magnitude": 4.5,
        "regional_maximum_distance_km": 1000.0,
        "surface_wave_velocity_range_km_s": [2.5, 4.0],
        "post_arrival_coda_hours": 3.0,
    }
    event = datetime(2024, 1, 1, tzinfo=UTC)
    window_start = datetime(2024, 1, 1, 0, 20, tzinfo=UTC)
    window_end = datetime(2024, 1, 1, 1, 0, tzinfo=UTC)
    hit, reason, _, _ = event_station_candidate(event, 5.0, 100.0, window_start, window_end, rules)
    assert hit and reason == "regional_magnitude_distance_rule"
    miss, reason, _, _ = event_station_candidate(event, 4.4, 100.0, window_start, window_end, rules)
    assert not miss and reason is None
