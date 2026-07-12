# P3-WU15 time-dependent discrete source trajectory

Status: frozen-library prefix trajectory complete; validated PEGS templates,
real noise and held-out reliability evaluation remain unavailable.

The trajectory reruns the same versioned discrete source library at strictly
increasing, predeclared sample counts. Every point reports its physical decision
time since origin, winning library scenario, Mw and segment, null improvement,
second-best separation, uniqueness and included-sample count. Station masks are
sliced in place and never compacted.

An early winner may change as more data arrive; the API preserves that history.
No point is labelled a reliable magnitude estimate. Reliability must be computed
across completely held-out events with the existing MAE, high-risk sensitivity,
low-risk specificity, interval-coverage and persistence gates at fixed empirical
false-alarm performance.
