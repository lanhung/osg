# End-to-end research and delivery roadmap

Status: active  
Baseline date: 2026-07-12  
Execution order: Paper 1 -> Paper 2 -> Paper 3  
Parallel risk track: Paper 2 and Paper 3 data access begins immediately

This document is the project work-breakdown structure (WBS). A checkbox is closed only when its listed evidence exists in Git or an external-access decision is recorded in a manifest. Writing code is not, by itself, completion.

## Delivery policy

Every completed work unit follows this sequence:

1. Freeze inputs, outputs, units, conventions, benchmark, and tolerance.
2. Implement one bounded capability without unrelated changes.
3. Run unit, physics, regression, and data-quality checks as applicable.
4. Save compact evidence under `reports/` or `experiments/`; update manifests.
5. Review `claims.yml`, secrets, licenses, and large-file exclusions.
6. Commit a coherent change and push it to `origin/main`.

Git contains code, configuration, manifests, checksums, compact fixtures, metrics, plots suitable for review, and manuscript sources. Git does not contain credentials, restricted station data, raw bulk products, large NetCDF/HDF/Zarr outputs, or private keys. Those objects must live in approved external storage and be reproducible from manifests.

## Phase 0 — Governance, environment, and access (Weeks 1–2)

### 0.1 Repository and reproducibility foundation

- [x] Create package, test, configuration, workflow, paper, experiment, data, and report structure.
- [x] Lock claim boundaries and forbidden novelty statements in `claims.yml`.
- [x] Add repository-wide scientific and agent rules.
- [x] Add dependency-free CI foundation tests.
- [ ] Install `uv`, resolve dependencies, generate `uv.lock`, and run the complete test/lint suite.
- [ ] Build and smoke-test the CPU image on Vultr.
- [ ] Build and smoke-test the GPU image on AutoDL; record CUDA, driver, and framework compatibility.
- [ ] Add immutable image tags/digests and a machine inventory. (Vultr inspected and AutoDL placeholder recorded; AutoDL inspection and image digests remain.)
- [x] Add experiment metadata schema validation and a working workflow dispatcher.
- [ ] Demonstrate identical reference output on Vultr and AutoDL.

Evidence: CI run, lockfile, image digests, machine inventory, cross-machine regression report.

### 0.2 Literature and claims audit

- [ ] Obtain and read the complete 2026 Haikou iGrav-048 paper, including supplements. (VOR core methods/results and its numerical changes from the open preprint are audited; a locally checksummed complete VOR/supplement bundle remains unavailable.)
- [x] Audit whether it contains event-specific typhoon windows or component separation.
- [ ] Read and encode the Helgoland methods, geometry, filters, and reported uncertainties.
- [ ] Read the atmospheric/Newtonian-noise and Cosmic Explorer source methods used by Paper 1.
- [x] Read PEGSGraph and the Peru real-time implementation, including training/evaluation splits.
- [x] Build an initial structured evidence table: claim, closest prior work, difference, required experiment, citation.
- [x] Update `claims.yml` after evidence review; record audit date. (Independent human reviewer remains required.)

Evidence: `docs/literature_matrix.*`, source notes, updated claims audit metadata.

### 0.3 Paper 2 data Go/No-Go

- [ ] Freeze candidate SG stations and candidate typhoons before requesting data.
- [x] Determine IGETS product levels, nominal cadence, registration/SFTP access path, and public station table. (Station/file-specific terms remain after registration.)
- [ ] Request Haikou iGrav-048 gravity, colocated pressure, calibration, jump, maintenance, and timing logs.
- [ ] Request or inventory Wuhan/HUST and other coastal or regional SG data.
- [ ] Inventory colocated/nearby tide gauges and GNSS vertical displacement records.
- [ ] Define IBTrACS, ERA5, CMEMS, hydrology, and optional wave-product queries. (IBTrACS selection plus ERA5/CMEMS product IDs, roles, bounds and double-count gates are frozen; exact event dates, CMEMS variable audit and hydrology product remain.)
- [ ] Verify at least one station/three events or two stations/two events with required channels.
- [ ] Record a formal go, conditional-go, or no-go decision by the end of Week 2.
- [ ] If no-go, activate Helgoland code-validation track and narrow the Paper 2 claim.

Evidence: completed data manifest, correspondence/access log, event-station matrix, signed decision record.

### 0.4 Paper 3 data Go/No-Go

- [ ] Inventory stations in South China, Hong Kong, Taiwan, Philippines, Vietnam, and surrounding networks. (EarthScope query and conservative BH/LH triplet summarizer frozen; live execution and other FDSN centres remain.)
- [ ] Distinguish archived, downloadable, real-time-capable, restricted, and unavailable stations.
- [ ] Verify waveform epochs, sample rates, three-component channels, responses, and licenses.
- [ ] Define noise-window strata: season, day/night, calm sea, typhoon, urban/remote, outages.
- [ ] Select a published PEGS waveform benchmark and obtain a validated simulator.
- [ ] Freeze the realistic station list before network experiments.
- [ ] Record a formal go, conditional-go, or no-go decision by the end of Week 2.

Evidence: station manifest, response completeness report, noise sampling plan, simulator decision.

## Phase 1 — Shared physics and Paper 1 atlas (Weeks 3–8)

### 1.1 Units, coordinates, and analytic primitives

- [x] Establish SI physical constants and microgal conversions.
- [x] Define the point-mass local coordinate frame, vertical sign, observation geometry, and validation rules.
- [x] Implement point-mass gravity vector and vertical component.
- [x] Test zero mass, invalid coincidence, sign, symmetry, inverse-square scaling, and units.
- [x] Implement on-axis finite thin-disk analytic vertical gravity.
- [x] Implement off-axis disk numerical integration with convergence tests.
- [x] Implement finite rectangular surface-load integration.
- [x] Implement two-dimensional Gaussian surface anomaly integration.
- [x] Implement three-dimensional density-anomaly volume integration.
- [x] Verify disk, rectangle, and Gaussian far-field point-mass limits below 1% error at the frozen distance ratio.
- [x] Document density-compensation/cancellation tests for internal-wave-like dipoles.
- [x] Implement the analytic point-mass gravity-gradient tensor with an explicit derivative convention.
- [x] Implement deterministic gravity-gradient summation for discretized volume-density anomalies.
- [x] Verify gradient symmetry, vacuum trace, finite differences, sign, and inverse-cube scaling.
- [x] Propagate direct gravity-gradient observables through all six process primitives.

Evidence: physics APIs, tests, convergence tables, analytic validation report.

### 1.2 Gridded ocean loads and elastic response

- [ ] Define grid-cell area, coastline, missing-value, longitude-wrap, and Earth-shape conventions. (Planar, spherical, WGS 84, scalar load height and partial coastal-cell fractions complete; coastline dataset, geoid/bathymetry and within-cell sensitivity remain.)
- [x] Convert sea-surface height anomaly to surface mass density without treating wave height as mean load.
- [x] Implement gridded direct-attraction integration with chunking and deterministic summation.
- [x] Add planar and spherical geometry comparison and validity limits.
- [x] Define a load Green-function provider interface with provenance/version metadata.
- [ ] Integrate a mature elastic-load Green-function dataset or library. (LoadDef v1.2.2 selected; combined `gE` versus direct `gN` semantics, reference-frame separation, scientific-use gate and provisional normalized-table adapter are complete. Exact tag pin/checksum, installation, equation/sign audit and published benchmark remain.)
- [x] Preserve direct attraction, deformation, and potential response separately at the interface and output level.
- [x] Test mass conservation, sign, spatial convergence, domain truncation, and component sums for reference kernels. (Production datasets still require case-specific sensitivity.)
- [ ] Benchmark CPU, memory, and I/O; determine when AutoDL CPU resources are justified.

Evidence: gridded-load module, Green-function adapter, physics/regression tests, performance report.

### 1.3 Signal and instrument models

- [x] Define time series sampling, Fourier normalization, windowing, detrending, one-sided PSD, and explicit no-resampling gap conventions.
- [x] Implement time-to-frequency conversion with Parseval tests.
- [x] Implement transient matched-filter SNR.
- [x] Implement periodic/quasi-periodic coherent-integration SNR with explicit observation time.
- [x] Define detection threshold and false-alarm convention; separate illustrative and decision-grade SNR.
- [x] Create versioned instrument-curve schema with digitization/source uncertainty.
- [ ] Add superconducting, absolute, and cold-atom gravimeter models. (Traceable iGrav self-noise, AQG and FG5 scalar/band anchors loaded; empirical site curves, full PSD digitization, newer cold-atom/HUST instruments remain.)
- [ ] Add gravity-gradient/inertial sensor models where defensible. (Legacy atom-gradiometer and GOCE band anchors loaded with explicit limitations; modern ground/space instruments remain.)
- [ ] Add environmental channels from gravitational-wave/Newtonian-noise literature without claiming reinvention. (Brundu atmospheric and Cosmic Explorer component/input manifests audited with observable separation; equation implementation and published-curve reproduction remain.)
- [x] Encode HUST facility capabilities from the official acceptance announcement, explicitly ineligible as a noise curve until frequency-dependent instrument evidence is obtained.

Evidence: PSD/SNR tests, instrument manifests, curve plots and provenance.

### 1.4 Six ocean-process models

- [ ] Tides: periodic surface-load parameterization and long-integration detectability. (Validated finite-disk direct-attraction primitive complete; elastic response, priors and detectability ensemble remain.)
- [ ] Storm surge/typhoon setup: regional sea-level anomaly with event-duration uncertainty. (Validated asymmetric finite-disk direct-attraction primitive complete; elastic response, spatial fields and cited priors remain.)
- [ ] Mesoscale eddy: Gaussian lens or 3-D density anomaly with compensation variants. (Validated translating SSH and exactly compensated 3-D core/halo variants complete; profile sensitivity and cited envelopes remain.)
- [ ] Internal wave: interface displacement/density dipole with cancellation diagnostics. (Validated mass-balanced oscillating 3-D Gaussian dipole complete; stratified eigenmode, free surface and cited priors remain.)
- [ ] Tsunami: long-wave transient parameterization with propagating source geometry. (Validated mass-balanced shallow-water Gaussian packet complete; realistic source/bathymetry, elastic response and cited priors remain.)
- [ ] Submarine landslide: coupled solid-water rapid mass migration with conservation checks. (Validated point-pair plus mass-balanced Gaussian continuum solid variants complete; entrainment/generated wave and cited scenarios remain.)
- [ ] Freeze realistic parameter priors and citations for every process. (M2, Helgoland, eddy, internal-wave, tsunami and small/giant landslide evidence anchors are encoded as non-probabilistic evidence. A strict joint-design gate reports 0/6 production-ready; coherent scenario families and remaining physics fields are still required.)
- [ ] Run Latin-hypercube or Monte Carlo uncertainty with deterministic seeds. (Validated deterministic linear/log Latin-hypercube and quantile engine complete; cited priors, correlations, convergence and production ensembles remain.)

Foundation milestone: registered experiment `P1-E001-foundation` runs all six direct-gravity primitives under explicitly non-scientific engineering fixture parameters; it is infrastructure evidence, not an atlas result.

Coverage milestone: registered experiment `P1-E002-detectability-foundation` applies the 90% energy-coverage gate to three vertical-gravity literature anchors. It classifies only the engineering landslide/iGrav pair; all long-period processes remain unknown/partial rather than extrapolated.

Gradient coverage milestone: registered experiment `P1-E003-gradient-detectability-foundation` applies the same gate to all six `Tzz` fixtures and only the two gradient-instrument anchors; vertical-gravity curves are explicitly excluded.

Evidence: process configs, prior table, unit/physics tests, compact ensemble metrics.

### 1.5 Published-case reproduction

- [ ] Reproduce Helgoland storm-surge gravity magnitude and deformation components. (Event/month targets, exact processing contract, input manifest and executable pending/pass/fail audit are frozen; IGETS/BSH/HELBH/GNSS inputs remain.)
- [ ] Quantify differences caused by geometry, resolution, Green functions, or domain truncation.
- [ ] Reproduce the Haikou NTOL magnitude/correlation only with legally available data or author-provided aggregates. (VOR—not preprint—targets, method contract, restricted/open input split and executable audit are frozen; SG/GNSS are author-restricted and exact CMEMS/MPIOM artifacts remain.)
- [ ] Record whether each case closes within 20–30% or supply a tested discrepancy explanation.
- [ ] Freeze compact regression fixtures from reviewed reproductions.

Evidence: reproducible case configs, metrics, plots, discrepancy report.

### 1.6 Atlas and Paper 1

- [ ] Produce frequency–equivalent-gravity panel with uncertainty.
- [ ] Produce distance–SNR panel with observation-time assumptions.
- [ ] Produce process–instrument detectability matrix.
- [x] Implement a frequency-coverage gate that forbids detectability classification when a curve covers less than the required signal-energy fraction.
- [ ] Produce uncertainty/cancellation panel.
- [ ] Classify detectable, boundary-detectable, and undetectable regions without censoring negative results.
- [ ] Run sensitivity to priors, geometry, PSD, integration time, and threshold.
- [ ] Generate all manuscript figures and tables from one registered workflow.
- [ ] Draft methods, results, limitations, data/code statements, and claim-safe abstract/title.
- [ ] Complete internal reproducibility review and freeze Paper 1 release candidate.

Evidence: registered experiment, figure/table bundle, full draft, reproduction report.

## Phase 2 — Paper 2 typhoon event attribution (Weeks 9–15)

### 2.1 Event catalogue and raw-data quality

- [ ] Select pilot event by expected load, station distance, track clarity, and channel completeness.
- [ ] Build event table with track, pressure, wind, distance, closest approach, landfall, surge, and coverage.
- [ ] Verify calibration, timing, missingness, outliers, earthquakes, jumps, maintenance, and drift.
- [ ] Generate raw/preprocessed time series and spectra at every correction stage.
- [ ] Freeze exclusion rules before comparing with ocean-model predictions.

Evidence: event catalogue, data-quality report, exclusion manifest.

### 2.2 Transparent SG correction chain

- [ ] Implement calibration and timing normalization. (Versioned feedback-voltage calibration with validity interval and propagated factor/offset uncertainty is complete; real calibration records and full timestamp normalization remain.)
- [ ] Flag spikes and earthquake-contaminated intervals without silently deleting them. (A frozen pre-comparison annotation policy, UTC interval ledger, overlapping flags and separate fit/metric masks preserve all original samples; real catalog/log review remains.)
- [ ] Represent gaps and uncertainty explicitly. (Cadence/gap segmentation plus a strict observation/component uncertainty budget with correlated groups are implemented; real gap decisions and uncertainty models remain.)
- [ ] Correct jumps and instrument drift with versioned decisions. (Explicit persistent-step decisions plus linear/quadratic drift models with UTC validity, allowed non-event fit roles, no extrapolation and propagated uncertainty are complete; real reviewed decisions/model parameters and sensitivity branches remain.)
- [ ] Remove solid Earth tide, ocean-tide loading, polar motion, atmosphere, and hydrology stepwise.
- [ ] Save every removed component and its contribution to the event peak. (The ordered waterfall preserves every input/removed/output series, provenance, effects, peak removal and RMS change; real-event artifacts remain.)
- [ ] Test alternative correction models and filter choices.

Evidence: correction waterfall, spectra, component files, sensitivity report.

### 2.3 Ocean-driven forward path and component closure

- [ ] Acquire and subset event-matched sea-level anomaly products.
- [ ] Calculate direct water attraction.
- [ ] Calculate vertical-deformation gravity effect and internal potential/mass response.
- [ ] Calculate atmospheric direct/loading terms and inverted-barometer response. (Hydrostatic pressure-to-column-mass and area-weighted, mass-conserving inverse-barometer primitives are complete; vertical atmospheric structure, elastic response, regional boundary validation and real fields remain.)
- [ ] Test CMEMS/ERA5 coupling to prevent double counting. (An executable effect-ownership ledger distinguishes missing, duplicate and ambiguous owners and currently blocks closure because the exact historical CMEMS inverse-barometer treatment is unknown; product metadata audit remains.)
- [ ] Estimate terrestrial precipitation/groundwater contribution. (Explicit groundwater-porosity conversion, a sign-audited infinite Bouguer-slab baseline, causal two-timescale rainfall storage, and uncertainty-aware correction adapter are complete; mixture-weight evidence, real data, finite catchment and elastic response remain.)
- [ ] Compare observation residual and independent forward prediction in time and frequency domains. (Mask-aware time-domain RMSE, correlation, peak amplitude and peak-time metrics plus a mask-aware Welch coherence reference implementation are complete; production FFT parity, frozen real-event frequency bands, and real-event comparison remain.)
- [ ] Close units, signs, timing, and uncertainty budgets. (SI/unit, component-collision, UTC-validity and correlated uncertainty gates exist; real component uncertainties, covariance assumptions and event closure remain.)

Evidence: component decomposition, double-count audit, closure metrics.

### 2.4 Multi-event evaluation

- [ ] Process at least 3–5 typhoons if the data gate permits.
- [ ] Add a non-typhoon strong-weather control.
- [ ] Add 3–5 quiet windows.
- [ ] Hold out at least one typhoon from all parameter fitting. (The attribution API freezes training event identities and rejects prediction on any training event; real event splits remain unavailable.)
- [ ] Report correlation, RMSE, peak amplitude/time error, explained variance, coherence, and event SNR. (Time-domain metrics including explained variance, paired held-out improvement, mask-aware coherence, leakage-safe attribution fitting, deterministic event-block coefficient bootstrap, and non-overlapping mask-aware event SNR are implemented; real PSD/band calibration and real-event reporting remain.)
- [ ] Report quiet-window false positives and held-out-event performance. (A split-safe calibration/held-out quiet-window audit reports monthly rates and refuses to pass when exposure cannot resolve the target rate; real quiet windows and held-out typhoons remain.)
- [ ] Run station, product, Green-function, hydrology, and filter sensitivity.
- [ ] Document failed events rather than excluding them post hoc.

Evidence: registered multi-event experiment, held-out metrics, false-positive table, failure log.

### 2.5 Paper 2 decision branches and manuscript

- [ ] Decide among successful attribution, ocean-product evaluation, non-detection constraints, or single-case short paper. (An executable claim-safe audit now selects these branches, keeps missing/fixture evidence pending, and separates scientific readiness from data-license release; real artifacts remain.)
- [ ] Ensure at least three of four novelty requirements are demonstrated; prefer all four. (The decision audit counts event attribution, direct/deformation separation, multi-source validation and cross-typhoon generalization, requiring at least three; none are claimed by the placeholder.)
- [ ] Generate six core figures and supporting diagnostics automatically.
- [ ] Draft claim-safe manuscript and explicitly distinguish the 2026 Haikou study.
- [ ] Complete internal reproducibility and data-license review.

Evidence: decision record, manuscript, figures, reproduction report.

## Phase 3 — Paper 3 regional PEGS warning value (Weeks 16–24)

### 3.1 Benchmark and Manila scenario library

- [ ] Reproduce a published PEGS event at specified stations/components.
- [ ] Achieve waveform correlation >0.95, amplitude error <10–20%, and onset error below one sample, or document justified revised tolerances.
- [ ] Extract published Manila source segments, geometry, slip, and location-specific tsunami-arrival distributions. (Strict source/arrival schema and source queue complete; full numeric extraction pending.)
- [ ] Record source-paper assumptions and avoid treating one 2.6-hour arrival as universal.
- [ ] Build 500–1000 baseline scenarios across Mw 8.0–9.0, segments, velocity, rise time, depth, dip, and heterogeneous slip.
- [ ] Preserve an interface for external tsunami calculations without claiming COMCOT simulation novelty.

Evidence: benchmark report, frozen scenario schema/table, simulator provenance.

### 3.2 Real station network and noise library

- [ ] Download permitted station metadata, responses, and waveform windows through manifests/scripts.
- [ ] Remove response and normalize components with timing checks.
- [ ] Label day/night, season, sea state, typhoon, urban/remote, gaps, and outages.
- [ ] Quantify PSD distributions, nonstationarity, transients, and cross-station correlation.
- [ ] Freeze training, validation, held-out dates, held-out segments, and domain-out events before modelling.
- [ ] Define existing, idealized, and incrementally augmented network variants.

Evidence: station/noise manifests, QC report, immutable split definitions.

### 3.3 Physics and statistical baselines

- [ ] Implement single-station amplitude/energy threshold baseline. (A mask-preserving sliding-RMS baseline freezes its threshold on calibration quiet windows and reports held-out quiet FAR, within-event trigger fraction and earliest triggering score index without mislabelling either as detection probability; response-corrected real waveforms, ensemble detection probability and passband evaluation remain.)
- [ ] Implement multi-station coherent stacking/template/likelihood baseline. (Aligned coherent stacking and a signed, noise-weighted sliding network-template statistic are complete under an explicit independent white-noise reference; physical sample/template/decision durations and per-station noise-calibration source IDs are mandatory. Validated PEGS templates, real cross-station covariance and likelihood comparisons remain.)
- [ ] Implement rapid source-parameter inversion for magnitude, region, and rupture segment. (A strict discrete template-library inversion reports winning library Mw/segment, null-model improvement and second-best ambiguity under an independent-noise reference; validated PEGS templates, continuous/source-uncertainty inference and real covariance remain.)
- [ ] Calibrate thresholds to false alarms per month/year using long real-noise windows.
- [ ] Generate time-dependent detection probability and reliable-magnitude timelines.
- [ ] Evaluate vertical-only versus three-component data.
- [ ] Evaluate 0%, 20%, and 40% station outage.
- [ ] Determine the physical detectability boundary before any GNN training.

Evidence: baseline metrics, calibration curves, boundary/negative-result report.

### 3.4 Network optimization

- [x] Define objective combining detection time, probability, false alarms, magnitude error, and station cost/count. (A deterministic non-dominated Pareto frontier is implemented; policy weights are deliberately not hidden in a scalar score.)
- [ ] Evaluate station-count/performance curves for existing and augmented networks.
- [ ] Identify robust station locations under rupture and noise uncertainty.
- [ ] Quantify minimum instrument/noise requirements by magnitude and segment.
- [ ] Test network recommendations against outages and high microseism/typhoon noise.

Evidence: Pareto curves, recommended network, uncertainty and robustness report.

### 3.5 GNN conditional stage

- [ ] Start only if real-noise multi-station baselines show stable information.
- [ ] Expand physically valid scenarios to 10,000–100,000 only after baseline validation.
- [ ] Define graph nodes, edges, features, targets, calibration, and uncertainty outputs.
- [ ] Overfit a tiny dataset as an implementation check.
- [ ] Train a complete single-GPU baseline before multi-GPU execution.
- [ ] Use multi-GPU only for seeds, cross-validation, and ablation.
- [ ] Compare against matched filtering/likelihood at identical splits and false-alarm constraints.
- [ ] Calibrate confidence and test held-out rupture segments, dates, stations, and out-of-domain sources.

Evidence: model/data cards, training metadata, seed runs, fair baseline comparison.

### 3.6 Warning utility and Paper 3

- [ ] Record origin, P trigger, PEGS detection, reliable magnitude, decision, and site-specific tsunami arrival times.
- [ ] Compare characterization time against P-wave, W-phase, and GNSS using defensible regional implementations.
- [ ] Report lead time distributions, not a single best-case number.
- [ ] Report detection probability at fixed false alarms, magnitude MAE/coverage, segment error, outages, and high-noise performance.
- [ ] Complete required ablations: synthetic/real noise, single/multi-station, existing/optimized, vertical/3C, physics/GNN, uniform/heterogeneous slip, calm/typhoon, full/outage.
- [ ] Convert negative results into explicit network and instrument requirements.
- [ ] Generate manuscript figures/tables through one registered workflow.
- [ ] Draft claim-safe manuscript and complete internal reproducibility review.

Evidence: warning-value experiment, ablation bundle, manuscript, reproduction report.

## Phase 4 — Programme integration and release

- [ ] Verify shared APIs and units are reused rather than copied among papers.
- [ ] Run all unit, physics, regression, workflow, and manuscript checks from clean environments.
- [ ] Reproduce all headline numbers and plots from immutable manifests/configs.
- [ ] Audit licenses, restricted-data boundaries, acknowledgements, and citation completeness.
- [ ] Create paper-specific code/data releases and archival checksums where permitted.
- [ ] Tag reviewed release candidates; push commits and tags to GitHub.
- [ ] Record unresolved limitations, failed scenarios, and follow-on work.

Evidence: clean-room reproduction report, release manifests, tags, final drafts.

## Current next work units

1. Push the repository foundation and this roadmap.
2. Implement point-mass gravity with explicit geometry/sign contracts and physics tests.
3. Implement the finite disk analytic benchmark and far-field comparison.
4. In parallel, turn Paper 2 and Paper 3 `unknown` data entries into concrete access decisions.
