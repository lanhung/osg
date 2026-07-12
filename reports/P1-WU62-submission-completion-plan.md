# P1-WU62 Paper 1 submission-completion plan

Date: 2026-07-12

Objective: advance Paper 1 from a claim-safe methods scaffold to a reproducible
submission candidate. A submission candidate requires completed scientific
figures and tables, registered production experiments, a compiled manuscript,
and no unresolved scientific gate hidden behind an engineering fixture.

## Current baseline

- Software/environment: pass (`438` tests plus `12` subtests locally and on
  AutoDL; locked Python 3.12 environment).
- Analytic and numerical primitives: pass for the direct-gravity and
  gravity-gradient foundation.
- Elastic provider: pass for the Paper 1 CE provider scope (50/50 published
  LoadDef rows for angle, radial displacement, and indirect elastic gravity).
- Process production readiness: fail (`0/6`).
- Final scientific figures: fail (`0/4`).
- Published cases: pending (Helgoland and Haikou).
- Manuscript: methods-first scaffold; Results and conclusions intentionally
  blocked.

## Work packages and acceptance criteria

### WP1 — Freeze six scientific scenario designs

For tide, storm surge, mesoscale eddy, internal wave, tsunami, and submarine
landslide:

1. Add traceable primary-source evidence for every varied physical parameter.
2. Choose either `probability_prior` or
   `sensitivity_design_not_probability`; no unsupported range may be labelled a
   percentile or prior.
3. Freeze parameter ranges, units, linear/log sampling, model variants, joint
   constraints, sample count, and integer seed.
4. Resolve each `unresolved_for_atlas` item by an implemented model choice,
   bounded sensitivity branch, or explicit exclusion from the Paper 1 observable.
5. Pass `audit_process_prior_readiness.py` at `6/6`.

### WP2 — Complete model and instrument coverage

1. Keep direct attraction, deformation, potential response, and displacement
   separate through all production outputs.
2. Add case-specific coastline/mask, grid-refinement, within-cell, and domain
   truncation checks for gridded loads.
3. Freeze instrument-specific empirical or literature noise curves with units,
   observable, frequency coverage, and digitization uncertainty.
4. Reproduce the selected environmental Newtonian-noise reference curve before
   using it in the environmental-channel panel.
5. Require the predeclared signal-energy coverage gate for every SNR
   classification.

### WP3 — Register and execute the production atlas

1. Create one immutable registered experiment covering all six processes,
   observables, distances, instruments, observation durations, model variants,
   and sensitivity samples.
2. Record commit, locked environment, manifests, seed, UTC start, machine, and
   outputs before execution.
3. Execute on AutoDL CPU resources; use GPUs only if a measured implementation
   is GPU-bound.
4. Pass deterministic reproduction, convergence, sensitivity, negative-result
   retention, and compact-output checksum gates.
5. Produce reviewed machine-readable metrics rather than copying values from
   exploratory notebooks.

### WP4 — Published-case gate

Helgoland:

1. Build the BSH fine/coarse-grid preprocessing, registered UTC trim, hourly
   snapshots, conservative remapping, direct attraction, and LoadDef elastic
   components.
2. Reproduce the published model amplitude and deformation within the frozen
   tolerance or quantify geometry/resolution/Green-function differences.
3. Evaluate observation correlation/RMS only if registered iGrav and the
   paper-equivalent 2022 processed GNSS series become available.

Haikou:

1. Acquire and checksum the exact legally available CMEMS/MPIOM artifacts.
2. Reproduce model-only values where the paper supplies sufficient targets.
3. Do not fabricate SG/GNSS reproduction; use the preregistered exception policy
   if observations remain author-restricted.

The case gate is complete only with a passing reproduction or a tested,
quantified discrepancy/availability disposition accepted by the registered
policy.

### WP5 — Final figures and tables

Generate from one registered workflow:

1. frequency–equivalent-gravity uncertainty panel;
2. distance–SNR panel with observation duration;
3. process–instrument classification matrix;
4. uncertainty/density-compensation panel;
5. validation and published-case tables;
6. supplementary convergence, coverage, and sensitivity figures.

Every asset must have a manifest entry with source experiment, checksum, units,
caption claims, and status `complete`. Visual inspection, text legibility, and
numerical cross-checks are required.

### WP6 — Manuscript completion

1. Replace every `\AtlasPending{}` marker with registered results or a
   defensible limitation.
2. Complete Introduction, Methods, Validation, Results, Discussion,
   Limitations, Data/Code Availability, abstract, captions, and bibliography.
3. Keep the title/claims inside `claims.yml`; do not add Paper 1 machine
   learning or unsupported novelty language.
4. Add exact Git release, data manifests, software environment, and reproduction
   command.

### WP7 — Submission audit and release

1. Build the PDF in a recorded TeX environment with no missing references,
   citations, figures, or overfull critical content.
2. Rerun lint, format, all tests, registered experiment reproduction, figure
   checksums, manuscript-claim tests, and clean-clone instructions.
3. Perform independent numeric consistency checks between metrics, tables,
   figures, abstract, and conclusions.
4. Freeze a release-candidate commit and push code/documents only; raw/restricted
   data remain off GitHub.

## Dependency order

`WP1 -> WP2 -> WP3 -> WP5 -> WP6 -> WP7` is the scientific critical path.
WP4 runs in parallel after its open-data preprocessing is implemented. Missing
restricted observations block only observation-based case statistics, not the
six-process production atlas.

## AutoDL execution policy

- Canonical code/configuration/manifests remain in the local Git repository and
  are synchronized to `/root/autodl-tmp/ocean-gravity-run/repo`.
- Bulk data and production outputs remain under the sibling AutoDL data/output
  directories.
- Available storage at planning time is approximately 308 GB. Jobs must estimate
  output size before launch and retain compact reviewed metrics rather than
  unbounded intermediate arrays.
- CPU/memory benchmarks decide concurrency. The four RTX 5000 Ada GPUs are not
  used merely because they are present.

## Human/external dependencies

The following cannot be inferred or bypassed:

- IGETS registration/authenticated access for iGrav-047 Level 1;
- a paper-equivalent processed 2022 HELG/HEL2 coordinate series, unless the
  authors publish or provide it;
- author-restricted Haikou SG/GNSS observations;
- final author list, order, affiliations, acknowledgements, conflicts, and target
  journal formatting choices.

All other work packages should be completed before requesting these inputs as
the sole remaining submission blockers.
