# P3-WU09 multi-objective network frontier foundation

Status: implementation and unit validation complete; scientific candidates and
metrics pending the station/noise/simulator gates.

The network optimizer now preserves the Pareto frontier across:

- earliest reliable detection time (minimize);
- held-out detection probability (maximize);
- continuous-stream false alarms per 30 days (minimize);
- held-out magnitude MAE (minimize); and
- station cost (minimize).

No weighted scalar score is imposed. That avoids hiding a policy choice—for
example, how many seconds of earlier detection justify an extra station or a
higher false-alarm rate. Exact metric ties retain both station designs, and all
serialized output is ordered by network identifier.

This is a tested optimization primitive, not a network recommendation. Real
candidate stations, empirical noise, source scenarios, response completeness,
latency, outage masks, and the registered Paper 3 gates must be supplied before
the frontier has scientific meaning.
