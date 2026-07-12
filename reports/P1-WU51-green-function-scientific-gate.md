# P1-WU51 production Green-function scientific-use gate

Status: gate implementation complete; LoadDef remains correctly not ready.

A provider can now be promoted from fixture/engineering use to scientific use
only when a separate immutable audit records and matches:

- provider ID and version;
- exact 40-character source commit;
- 64-character artifact SHA-256;
- licence;
- Earth model and CE/CM/CF reference frame;
- per-source-kilogram normalization;
- combined or genuinely decomposed component semantics;
- angular distance in radians;
- completed source/equation audit; and
- a passed, identified published benchmark.

Provider metadata and audit metadata must match field by field. A correct-looking
version string cannot substitute for a commit/checksum, and installing LoadDef
will not by itself make the provider scientifically eligible.

The selected LoadDef entry remains `not-ready`: source commit, artifact checksum,
reference frame, equation audit and benchmark evidence are still absent because
the upstream source cannot be retrieved through the current DNS-restricted
control plane. This is an explicit failed gate, not missing bookkeeping.
