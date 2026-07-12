# P1-WU57 LoadDef v1.2.2 source and execution audit

Status: exact source, environment, equation semantics, normalization and PREM
engineering execution passed; published benchmark and reference-frame decision
remain open, so scientific use is still disabled.

The lightweight `v1.2.2` tag resolves to commit
`b65493574f606b7d165a2d10fe862eda5b32f89a`. The 31,626,039-byte GitHub tag
archive has SHA-256
`77243146b260c6ff90d09cdeda6f721c6e8e3c003899614dab5e345c66611b5b`.
Its GPL-3.0 license file and bundled PREM input are independently checksummed in
the run configuration. The archive, extracted source, environment and bulk
outputs remain on AutoDL; only configuration, provenance and compact evidence
are stored locally.

An isolated Python 3.12.12 environment freezes MPICH 5.0.1, mpi4py 4.1.2,
NumPy 1.26.4, SciPy 1.11.4, Numba 0.63.1 and Matplotlib 3.10.8. A two-rank smoke
run completed degrees 0 through 20. The upstream-defined undefined cells are
LLN degree-zero asymptotic columns and degree-one potential/shear coefficients;
all other smoke values are finite.

The production run used 32 MPI ranks and generated all four PREM Love-number
tables for degrees 0 through 10,000. Each table has exactly 10,001 consecutive
degree rows and only the declared undefined cells. At degree 10,000, the three
load Love numbers differ from the upstream asymptotic columns by approximately
`8.83e-8`, `1.17e-7`, and `1.36e-7` relative. The compact diagnostic metrics on
AutoDL have SHA-256
`394ec05e756cd8ebdf15e5997310790c8219fbbbcfb5907d1fb2513b28b8f9ff`.

Eight configured angular distances from 0.0001 to 180 degrees were then run for
CE, CM and CF reference frames. Every table has 8 rows and 12 finite columns.
The project adapter reverses the exact upstream
`gE * 1e18 * (a * theta_rad)` normalization. Independently evaluating the
source `gN` equation gives a maximum relative difference of `5.54e-6`, within
the precision of the upstream four-decimal scientific-notation output. The
compact Green-function diagnostic metrics have SHA-256
`bec8f7031a9185c62b59ed43c4bfeb8add67bf4693038d943e714f81ce61f6a0`.

Source lines establish that `gE` combines the vertical-displacement/free-air
term with the potential-Love-number response, whereas `gN` is direct Newtonian
attraction. Therefore the project must use `gE` as the combined elastic response
and retain its independent direct-attraction calculation; adding LoadDef `gN`
would double count direct attraction.

This is an engineering and equation audit, not the required published-case
validation. A CE/CM/CF convention must still be selected for the paper, and a
published LoadDef/Guo or SPOTL benchmark must pass a tolerance frozen before
comparison.
