# Paper 1 AI scientific review record

- Reviewer: OpenAI Codex (AI system; non-human)
- Affiliation and ORCID: none
- Review role: user-authorized independent-expert-style scientific audit
- Prior project involvement: yes; the same AI system assisted implementation
- Independence limitation: this is not independent human peer review
- Initial review date: 2026-07-13
- Journal-revision review date: 2026-07-20
- Corrective experiments: `P1-E010-independent-review-sensitivity` and
  `P1-E011-temporal-spectral-convergence`
- Conflict declaration: implementation involvement is a methodological conflict
- Permission to acknowledge by name: not applicable

## Recommendation

**Scientifically suitable as a Journal of Geodesy release candidate after the
recorded author declarations, archival DOI and clean journal-PDF build are
complete.**

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
   Helgoland records, P1-E006/E008/P1-E010 production metrics, observable ledger
   and literature matrix.
6. P1-E011's 1,446-record boundary-aware finite-DTFT audit, analytic-source
   cadence tests and six process-specific record-window designs.
7. Journal of Geodesy editorial policy, DOI `10.1007/s00190-021-01515-7`, which
   requires an Author Contribution Statement and Data Availability Statement
   while recognizing that not all geodetic data can be publicly redistributed.
8. Antokoletz et al. (2024), DOI `10.1093/gji/ggad371`, confirming the formal
   volume-year/page metadata and the need for composition-aware atmospheric and
   non-tidal ocean-loading corrections in precision gravity time series.

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

### 5. Native Fourier-bin and record-window dependence — resolved by claim revision

The former headline values for eddy, internal wave, landslide and tsunami were
at or near their first native positive-frequency bin, and the storm value was
near its second bin. P1-E011 therefore tested 1x/4x/16x/64x finite-DTFT sampling,
1x/2x/4x/8x analytic-source cadence and physically defined window families.
All six process medians pass the final grid-convergence gate, all five
regenerable process families pass cadence convergence, and no record reaches
90% coverage after boundary-aware dense integration.

Tide and internal-wave estimates pass the fixed window-stability gate. Eddy,
storm surge, tsunami and landslide do not: approximately constant
$f_{\rm low}T$ shows that their exact lower edge remains partly a record-window
quantity. The revised abstract, results, Figure 3, discussion and conclusions
therefore retain the common-support deficit but stop calling the four exact
values process-intrinsic measurement requirements. This is the scientifically
correct disposition and removes the strongest technical objection to the
journal draft.

### 6. Journal fit and remaining non-scientific gates

The paper now addresses gravity-field modelling, time-variable gravity,
loading-response semantics and measurement-evidence support, all within the
journal's geodetic scope. Its novelty is not the tautology that frequency bands
must overlap; it is the component-resolved, cross-process quantification and the
demonstration that apparently precise low-frequency requirements can themselves
be finite-window artifacts. The 50-row LoadDef comparison and Helgoland
model-scale consistency check are adequate for a methods/framework paper so
long as no observation-correlation validation is claimed.

The remaining blockers are editorial/ownership matters, not additional
scientific computation: all authors must approve the CRediT statement, funding
and competing-interest declarations; an archival DOI must exist; and the actual
journal main/SI PDFs must complete a clean LaTeX/BibTeX build. These cannot be
inferred by an AI reviewer.

## Gate decision

- Scientific major issues dispositioned: yes
- E011 convergence and window-dependence gate: pass
- Journal-scope and claim calibration: pass
- Author contribution/declaration approval: pending authors
- Archival DOI and final clean PDF: pending release workflow
- Major issues dispositioned: yes
- Human-independent identity requirement met: no
- User-authorized AI scientific audit completed: yes
- Internal G8 disposition: pass with explicit AI-substitution disclosure
