# P1-WU58 published LoadDef provider benchmark

Status: Paper 1 CE provider-scope benchmark passed; broader twelve-column
comparison failed and is retained as a discrepancy.

The open Europe PMC supplementary bundle for Martens et al. (2019), DOI
`10.1029/2018EA000462`, was downloaded only to AutoDL. Its SHA-256 is
`fe068554f11ac91e127affec5a1497994b6c2022b8fd49a34823ce7c6ce58b15`.
The bundle contains the exact published oceanless PREM input, degrees 0 through
10,000 Love-number table, and 50-row CE, CM and CF Green-function tables.
Individual file checksums are frozen in the local run configuration.

The first predeclared criterion required every numeric output token in the Love
number and twelve-column Green tables to match exactly after ignoring text
headers and timestamps. It failed: 8,841 row keys contained at least one token
difference. This failure is not relabeled as a pass. A discrepancy audit found
maximum Love-number relative differences of `4.65e-8` for h, `2.11e-7` for l,
and `6.17e-8` for k; all three asymptotic columns match exactly. Green-function
differences occur only in tilt and strain columns, reaching `0.0033` in a
normalized strain value at 180 degrees.

The project interface had already been restricted to angular distance, radial
displacement and combined elastic gravity `gE`; it does not consume tilt or
strain. A second scope-specific criterion was therefore frozen before a new
50-angle run: all three provider columns must match the published numeric tokens
exactly for CE, CM and CF. New Green tables were generated at all 50 published
angles. All 450 frame/angle provider records match exactly, with zero missing
angles and zero token mismatches. The comparison metrics SHA-256 is
`57f1005d0fd4b2a2fbf87808e47d76b4f4886fdb87dcc22ca43e5196c6ab8daf`.

Paper 1 freezes the CE frame because the paper's Figure 2 comparison against
Guo et al. (2004) uses CE and the published CE table is reproduced exactly over
the project provider scope. This authorization does not extend to LoadDef tilt
or strain, and it does not remove the CE/CM/CF sensitivity requirement for
Paper 2 observational analyses.
