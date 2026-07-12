# P1-WU64 Helgoland BSH model reproduction

Date: 2026-07-12

Registered experiment: `P1-E005-helgoland-bsh-model`

## Result

The open-data, model-only branch passes its predeclared validation target. The
runner processed all 242 registered BSH-HBMnoku files into 720 unique hourly
samples on a 1/8-degree grid. Fine-grid loads replaced 1,725 target cells wholly
inside the fine source domain; the remaining cells came from the coarse domain.
Remapping integrates source cell means over exact WGS84 area intersections.

The fitted BSH gravity-to-height ratio is
`-2.2662457310207795 nm s^-2 per mm` in the paper convention (gravity increase
positive downward and displacement positive upward). Voigt et al. (2024)
report `-2.684 nm s^-2 per mm`. The fractional difference is `0.155646`, below
the registered `0.20` tolerance for the declared LoadDef PREM/CE versus SPOTL
Gutenberg-Bullen and 30-day versus three-year detiding differences.

## Component discipline

The registered artifact retains separate 720-point series for:

- direct geodetic-up Newtonian attraction;
- LoadDef CE combined elastic gravity (deformation plus potential response);
- vertical displacement.

The direct component is not added to the published height-independent loading
comparison. The sign conversion is applied only at the published ratio boundary
and is recorded in machine-readable metrics.

## Scope and remaining observation gate

The paper's `85 nm s^-2` gravity range and `-34 mm` displacement are observed
iGrav047 and HELG extrema, not published BSH model acceptance values. They are
therefore retained only as observation context. Correlation and RMS-reduction
reproduction remains unclassified until authenticated iGrav Level 1 and a
paper-equivalent processed 2022 GNSS series are legally available.

The source paper used a three-year ET34-X-V80 tidal analysis. This experiment's
30-day harmonic fit is transparent and deterministic but not claimed to be
equivalent.
