# Paper 1 AI scientific review record

- Reviewer: OpenAI Codex (AI system; non-human)
- Affiliation and ORCID: none
- Review role: user-authorized independent-expert-style scientific audit
- Prior project involvement: yes; the same AI system assisted implementation
- Independence limitation: this is not independent human peer review
- Review date: 2026-07-13
- Manuscript baseline: Git commit `4bd2f36`
- Corrective experiment: `P1-E010-independent-review-sensitivity`
- Conflict declaration: implementation involvement is a methodological conflict
- Permission to acknowledge by name: not applicable

## Recommendation

**Release as a versioned technical preprint after the recorded corrections.**

Do not describe this record as external human peer review. A journal submission
still requires real author identities, affiliations, declarations and author
approval of the target-journal files.

## Evidence checked

1. Voigt et al. (2024), DOI `10.1029/2024GL109262`: the published
   -2.684 nm s^-2 mm^-1 ratio is derived from BSH height-independent gravity
   after local direct Newtonian attraction is reduced.
2. Martens et al. (2019), DOI `10.1029/2018EA000462`: LoadDef distinguishes CE,
   CM and CF frames and publishes radial displacement and elastic gravity `gE`
   Green-function benchmarks.
3. Schäfer et al. (2020), DOI `10.1093/gji/ggaa359`: iGrav015/iGrav032 average
   self-noise is about -180 dB over 1e-3--1e-1 Hz at J9 under the three-channel
   correlation method.
4. Ménoret et al. (2018), DOI `10.1038/s41598-018-30608-1`: the AQG/FG5 constant
   PSD interval is 5e-4--1e-2 Hz, while longer timescales are not white noise.
5. The repository's analytic tests, 50-row LoadDef benchmark, P1-E005/E009
   Helgoland records, P1-E006/E008 production metrics, observable ledger and
   literature matrix.

## Major findings and dispositions

### 1. Instrument-band provenance — resolved

The earlier AQG/FG5 lower edge of 1e-3 Hz was a disclosed project choice, but
the primary source supplies a narrower explicit white-noise plateau beginning
at 5e-4 Hz. The release now uses exactly 5e-4--1e-2 Hz. Frozen P1-E006/E008
outputs remain unchanged; P1-E010 is the registered corrective audit.

### 2. Spectral-convention sensitivity — resolved

The earlier text did not expose enough of the finite-record energy convention.
The manuscript now defines cumulative coverage mathematically. P1-E010
reconstructed all 1,446 records and compared the registered rectangular-window
trapezoid with rectangular and periodic-Hann periodogram bin sums. All six
median 90% requirements remain below 5e-4 Hz. The largest shift is the internal
wave rectangular-bin result, 2.20e-5 Hz versus 1.10e-5 Hz registered, which does
not change the coverage conclusion.

### 3. Helgoland observable semantics — acceptable with caveat

The comparison is valid only for the combined elastic/height-independent
gravity component. The direct-plus-elastic arithmetic result is informative
but unauthorized. The 15.56% residual cannot be allocated between the Earth
model and detiding changes with current runs. The manuscript now states all
three boundaries.

### 4. Generality — acceptable for the revised title

The 1,446 records are repeated scenario/distance/duration designs, not 1,446
natural events. The source models are representative benchmarks. The title,
Table 1 and limitations no longer imply a complete detectability atlas or
natural-population distribution.

## Gate decision

- All 15 checklist items answered: yes
- Major issues dispositioned: yes
- Human-independent identity requirement met: no
- User-authorized AI scientific audit completed: yes
- Internal G8 disposition: pass with explicit AI-substitution disclosure

