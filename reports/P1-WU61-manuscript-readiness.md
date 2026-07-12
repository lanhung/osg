# P1-WU61 Paper 1 manuscript readiness

Date: 2026-07-12

Decision: Paper 1 is ready for a methods-first internal or pre-submission draft,
but it is not ready for a submission-complete Results section or scientific
conclusion.

## Evidence already sufficient for drafting

- The novelty boundary, title, required demonstrations, and prohibited claims
  are locked in `claims.yml` and enforced by manuscript tests.
- Direct gravity, gravity-gradient, planar/spherical/ellipsoidal grids, process
  primitives, spectra, SNR, quality annotations, and instrument curves have
  analytic or behavioral tests.
- The Python 3.12 environment is locked, the registered foundation experiments
  reproduce, and the local and AutoDL suites pass 438 tests plus 12 subtests.
- LoadDef v1.2.2 was installed from a checksum-pinned source archive in an
  isolated environment. The project-provider fields used by Paper 1---angle,
  radial displacement, and indirect elastic gravity in the CE frame---match all
  50 published Martens et al. rows exactly.
- HELBH, both BSH-HBMnoku SSH grids, and HELG/HEL2 raw GNSS inputs for the
  Helgoland window are acquired on AutoDL with checksums and structural audits.

These results support writing the Introduction, Methods, software validation,
data/code availability, and a transparent limitations section now.

## Gates that prohibit a submission-ready result claim

1. `reports/process_prior_readiness.json` reports 0/6 process families ready for
   a production ensemble. Every family still lacks a frozen joint design and has
   unresolved physics or parameter fields.
2. `papers/paper1_atlas/figure_manifest.json` contains no complete scientific
   figure. Two figures are engineering prototypes and two await production
   ensembles or cited parameter envelopes.
3. P1-E001 through P1-E004 are explicitly engineering references. Their values
   cannot populate the manuscript Results section.
4. The preregistered published-case gate is incomplete. Helgoland still lacks
   registered iGrav access and a paper-equivalent processed 2022 GNSS series;
   Haikou still lacks the restricted observations and exact open model artifacts.
5. Author list, affiliations, TeX build environment, final bibliography review,
   production tables, and final figure assets remain pending.

## Minimum completion path

1. Resolve and cite the remaining physics/parameter fields, freeze one joint
   production design for each of the six process families, and rerun the prior
   readiness audit to 6/6.
2. Register and execute the production atlas ensembles with realistic
   instrument-specific noise, bandwidth, observation duration, density
   compensation, and negative-result retention.
3. Complete or formally disposition the two published-case gates under the
   preregistered exception policy; restricted access cannot be replaced by a
   simplified proxy.
4. Generate all four final figures and result tables from registered commits and
   immutable manifests, then replace every `\AtlasPending{}` marker.
5. Compile and review the manuscript in a recorded TeX environment before
   labeling it a submission draft.

Until these steps are complete, the defensible manuscript status is
"methods-first working draft," not "paper completed."
