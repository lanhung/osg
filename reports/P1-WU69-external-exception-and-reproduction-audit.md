# P1-WU69 External exception and reproduction audit

Date: 2026-07-12

The machine-readable published-case submission policy passes. It requires at
least one passing open model case; `P1-E005` supplies that case through the
Helgoland BSH gravity-to-height validation. Helgoland observation statistics and
the Haikou model/observation reproduction are disclosed as unavailable supporting
evidence and do not block the main six-process atlas. The policy prohibits
imputing their correlation, RMS or observation-extreme values.

The two scientific Paper 1 experiments were rerun through the registered
workflow on AutoDL:

- `P1-E005-helgoland-bsh-model` reproduced SHA-256
  `7c5535c31a96e88b1a807b14c7182922c3bbfdf42b6bde0112dec9bbf7f09da9`;
- `P1-E006-evidence-bounded-atlas` reproduced SHA-256
  `6d8235af08f52bb2c295f9bd53014f3194855d8936adbc4dd47a26c4af4483e5`.

Both are byte-identical to their registered metadata. The figure renderer also
reproduces identical asset checksums, and the final manuscript TeX log contains
no undefined references or citations.

This closes all current reproducibility work that is independent of structural
model variants and human author/journal decisions. It does not waive the
remaining model-variant sensitivity gate or constitute independent human peer
review.
