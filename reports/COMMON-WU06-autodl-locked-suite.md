# COMMON-WU06 AutoDL locked-suite validation

Status: AutoDL execution gate passed; container-image and two-host parity gates
remain open.

The local working tree was synchronized to an isolated AutoDL execution copy,
excluding Git metadata, virtual environments, local tool caches, raw/derived
data, and output directories. The server uses Python 3.12.12 with uv 0.8.24 and
the exact `uv.lock` environment. Data and logs remain under
`/root/autodl-tmp/ocean-gravity-run`; only compact registered metrics and
provenance are retained in the local repository.

The complete validation run passed:

- 430 pytest tests and 12 subtests;
- Ruff lint and format checks;
- source, test, and script compilation;
- all five experiment metadata/checksum validations; and
- exact reproduction of P1-E001 through P1-E004 and P3-E001 registered outputs.

The validation log SHA-256 is
`3a65b41290c52b6e8ecf206554d578f54009824094682625c320258a9967ab91`.
The bulk log is intentionally retained only on AutoDL at
`outputs/full-validation-canonical-2026-07-12.log`.

The initial run found non-identical P1-E002/P1-E003 hashes caused by platform
`cmath/libm` differences in DFT-scale numerical leakage (coverage near `1e-29`)
and final floating-point digits. The scientific status labels were identical.
The registered configuration now declares a `1e-24` numerical coverage floor
and 10 significant report digits. Calculations retain full precision; only the
reporting boundary is canonicalized. Unit tests freeze both rules.

This evidence does not establish a GPU framework or immutable image digest:
PyTorch is not installed in the locked physics environment. It also does not yet
prove two-host identity for the revised canonical artifacts, because the user
required execution to remain on AutoDL during this work unit. A future approved
Vultr rerun must reproduce the revised hashes before closing that roadmap item.
