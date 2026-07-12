# Ocean Gravity Program

Reproducible research code for three connected studies:

1. a frequency-distance-instrument detectability atlas for ocean-induced gravity signals;
2. event-resolved attribution of typhoon-driven ocean mass loading in superconducting gravimeter records;
3. detectability and warning value of prompt elasto-gravity signals (PEGS) from Manila Trench earthquakes.

The project is gated by scientific evidence, not by code completion. The authoritative novelty boundaries are in [`claims.yml`](claims.yml), and data access risks are tracked in [`data/manifests/data_availability.yml`](data/manifests/data_availability.yml).

## Quick start

The supported runtime is Python 3.11 or newer. With `uv` installed:

```bash
uv sync --group dev
uv run pytest
uv run ruff check .
```

The dependency-free foundation tests can also run on a bare Python installation:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Reproducibility contract

Large data never enters Git. Each dataset is represented by a manifest containing its source, time range, access status, license, and checksum. A formal experiment must record the Git commit, environment, data manifest, configuration, random seed, machine, and output files.

The intended reproduction interface is:

```bash
make reproduce PAPER=2 EXP=P2-E017
```

It is operational for registered deterministic experiments containing `experiments/paperN/<experiment-id>/metadata.json`, a versioned runner/config, and expected output SHA-256. Unregistered experiments fail explicitly instead of silently producing an untracked result.

## Repository map

- `src/oceangravity/`: reusable physics, instruments, processing, PEGS, and evaluation code.
- `configs/`: versioned paper-specific parameters.
- `data/manifests/`: metadata only; raw and derived data are ignored.
- `experiments/`: experiment definitions and compact metrics, not bulk outputs.
- `tests/unit/`: software behavior; `tests/physics/`: analytic and literature benchmarks; `tests/regression/`: frozen numerical results.
- `papers/`: manuscript sources and figure specifications.
- `reports/`: generated summaries and validation reports.

## Immediate gates

- Gate 0: lock claims against nearest prior work.
- Gate 1: pass analytic, limiting-case, and published-case validation.
- Gate 2: document missingness, outliers, jumps, timing, spectra, and exclusions.
- Gate 3: predefine success and failure criteria.
- Gate 4: test alternatives, sensitivity, holdouts, uncertainty, and failure cases.
