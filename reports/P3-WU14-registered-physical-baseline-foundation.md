# P3-WU14 registered physical-baseline foundation

Status: deterministic Paper 3 engineering experiment registered and reproducible;
no real PEGS detectability evidence is claimed.

`P3-E001-physical-baseline-foundation` connects the single-station quiet-threshold
audit, two-station signed template score and discrete source-library inversion in
one checksummed workflow. The exact fixture recovers its embedded Mw 8.6 central-
segment template and demonstrates coherent score growth.

The experiment intentionally fails scientific readiness. Four held-out quiet
scores at a 60-second decision step can only resolve a nonzero rate of 10,800
false alarms per 30-day month, far above the one-per-month target. It also uses
engineering waveforms and independent synthetic noise. These blockers are saved
in `metrics.json`, preventing the successful fixture inversion from being quoted
as regional warning performance.

Reproduce it with:

```bash
make reproduce PAPER=3 EXP=P3-E001-physical-baseline-foundation
```
