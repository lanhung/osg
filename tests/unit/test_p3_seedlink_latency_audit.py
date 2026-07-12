import numpy as np
from obspy import Stream, Trace, UTCDateTime

from scripts.audit_p3_seedlink_latency import summarize_stream


def test_empty_stream_has_no_invented_latency() -> None:
    result = summarize_stream(Stream(), UTCDateTime("2026-01-01"))
    assert result == {
        "status": "no_packets",
        "trace_count": 0,
        "latest_end_utc": None,
        "lag_seconds": None,
    }


def test_latency_uses_latest_trace_end() -> None:
    trace = Trace(data=np.zeros(4))
    trace.stats.starttime = UTCDateTime("2026-01-01T00:00:00Z")
    trace.stats.sampling_rate = 1.0
    result = summarize_stream(Stream([trace]), UTCDateTime("2026-01-01T00:00:10Z"))
    assert result["lag_seconds"] == 7.0
    assert result["total_samples"] == 4
