# COMMON-WU05 locked scientific environment

Status: uv lock, Python 3.12 local environment, complete pytest and Ruff gates
established; Docker images and AutoDL cross-machine parity remain.

The repository now pins a resolved scientific environment in `uv.lock` and
declares Python 3.12 as the local default. The validated control-plane
environment uses uv 0.8.24, CPython 3.12.11, ObsPy 1.5.0, NumPy 2.5.1, SciPy
1.18.0 and Xarray 2026.7.0. ObsPy is the required MiniSEED, StationXML and
instrument-response implementation; no custom binary parser substitutes for it.

The complete pytest suite passes in the locked environment. Ruff was run for the
first time across source, scripts and tests; legacy findings were fixed and both
`ruff check` and `ruff format --check` are now release gates. GitHub Actions
installs the fixed uv version, syncs the lock and runs these gates on Python 3.11
and 3.13 in addition to the dependency-free unittest and experiment-registry
checks.

This does not establish container or GPU reproducibility. CPU/GPU image digests,
AutoDL inspection and identical cross-machine experiment output remain open.
