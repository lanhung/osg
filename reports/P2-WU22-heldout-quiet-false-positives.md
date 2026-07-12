# P2-WU22 held-out quiet-window false positives

Status: split-safe quiet-window audit complete; real quiet scores pending data.

Quiet score windows have immutable identities and roles: threshold calibration or
held out. The empirical threshold is selected using only calibration scores and
then applied unchanged to all held-out windows. Every window must use the same
decision step.

The audit reports calibration and held-out IDs, total held-out scores,
exceedances, which held-out windows triggered, false alarms per 30-day month, and
the minimum nonzero rate resolvable from the held-out record length. Passing
requires the observed held-out rate to meet the same target used for calibration
and the held-out exposure to resolve a nonzero rate at least as small as that
target.

This does not make short quiet windows sufficient evidence. When their nonzero
rate resolution is coarser than the target, zero exceedances explicitly fail the
decision gate. Real Paper 2 evaluation still requires frozen scoring,
non-overlapping quiet dates and a defensible decision cadence.
