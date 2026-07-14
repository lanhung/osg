# End-to-end research and delivery roadmap

Status: active  
Baseline date: 2026-07-12  
Scientific delivery order: Paper 1 -> Paper 2 -> Paper 3
Execution model: Paper 1 sprint plus immediate Paper 2 authorization, Paper 3
simulator/noise validation, and infrastructure risk-control tracks

This document is the project work-breakdown structure (WBS). A checkbox is closed only when its listed evidence exists in Git or an external-access decision is recorded in a manifest. Writing code is not, by itself, completion.

The delivery order does not make external approvals sequential dependencies. Human
authorization and simulator/data acquisition begin at baseline and run beside the
Paper 1 scientific sprint. Owners, hard dates, and fallback triggers are authoritative
in `data/manifests/critical_path.yml`.

## Critical-path operating decision

- Paper 1 remains the near-term scientific result and does not acquire an AI stage.
- Paper 2 station access is a PI-owned external-authorization track starting on Day 0.
  Codex may prepare inventories, manifests, and correspondence drafts, but cannot
  register identities, accept agreements, or state that a request was sent.
- Paper 3 published-waveform reproduction moves from a Week 16 activity to an
  immediate parallel validation track. Benchmark specification, simulator acquisition,
  and numerical reproduction are separate gates.
- Real continuous PEGS-band noise and response-corrected waveforms are a second
  long-lead risk beside SG authorization; StationXML alone does not close this gate.
- GNN work remains conditional on a validated simulator and stable information in
  real-noise, multi-station physical/statistical baselines.
- Infrastructure backup and cross-machine checks are urgent risk controls but are not
  counted as scientific-result completion.
- The 6--7 month target is conditional on raw-enough SG data closing within 4--8
  weeks and the PEGS benchmark/simulator path closing within about 4 weeks. A missed
  hard trigger activates a documented fallback rather than indefinite waiting.

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
- [x] Install `uv`, resolve dependencies, generate `uv.lock`, and run the complete test/lint suite. (Local uv 0.8.24/Python 3.12 environment and Python 3.11/3.13 CI matrix are frozen; container parity remains separate.)
- [ ] Build and smoke-test the CPU image on Vultr.
- [ ] Build and smoke-test the GPU image on AutoDL; record CUDA, driver, and framework compatibility.
- [ ] Add immutable image tags/digests and a machine inventory. (Vultr and AutoDL are inspected; immutable CPU/GPU image digests remain.)
- [x] Add experiment metadata schema validation and a working workflow dispatcher.
- [ ] Demonstrate identical reference output on Vultr and AutoDL. (All five registered outputs reproduce on AutoDL after canonical reporting rules were frozen; the revised hashes still require a Vultr rerun.)

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

Owner: PI for identity, agreements, and station contact; Codex for inventories,
manifests, closure audits, and analysis readiness.

- [ ] Freeze candidate SG stations and candidate typhoons before requesting data. (The 11-event Haikou-proxy list remains only a collaboration inquiry. A 2026-07-14 official-table/IBTrACS acquisition screen now prioritizes Hsinchu, Matsushiro/Mizusawa and Wuhan, but authenticated Level 1 file coverage, headers and station logs must close before final station/event freeze.)
- [x] Determine IGETS product levels, nominal cadence, registration/SFTP access path, and public station table. (Station/file-specific terms remain after registration.)
- [ ] Request Haikou iGrav-048 gravity, colocated pressure, calibration, jump, maintenance, and timing logs.
- [ ] Request or inventory Wuhan/HUST and other coastal or regional SG data.
- [ ] Inventory colocated/nearby tide gauges and GNSS vertical displacement records.
- [ ] Define IBTrACS, ERA5, CMEMS, hydrology, and optional wave-product queries. (The live checksummed IBTrACS archive and 48-event broad South China Sea inventory now freeze exact dates; ERA5/CMEMS product IDs, roles, bounds and double-count gates are frozen. SG-linked shortlist, exact CMEMS variable audit and hydrology product remain.)
- [ ] Verify at least one station/three events or two stations/two events with required channels.
- [ ] Record a formal go, conditional-go, or no-go decision by the end of Week 2.
- [ ] If no-go, activate Helgoland code-validation track and narrow the Paper 2 claim.

Hard triggers from the 2026-07-12 baseline:

- 2026-07-19 (Day 7): finish the registered-access IGETS station/product inventory.
- 2026-07-26 (Day 14): complete the first PI follow-up for Haikou/Wuhan requests.
- 2026-08-09 (Day 28): require a credible station, channel, terms, and delivery path;
  otherwise mark the preferred route conditional/no-go.
- 2026-08-23 (end Week 6): activate the best legally accessible substitute event/station
  if the preferred observations still have no committed delivery date.
- 2026-09-06 (end Week 8): stop allowing Haikou access to block method validation.

Fallback ladder, with claims narrowed at each step:

1. Haikou/Chinese coastal SG with multi-typhoon channel closure;
2. another coastal, typhoon-exposed SG with raw-enough gravity, pressure, logs, and
   independent environmental validation;
3. another tropical-cyclone event with equivalent data closure;
4. Helgoland or another storm-surge benchmark for method/model validation only,
   without a typhoon-generalization claim.

Evidence: completed data manifest, correspondence/access log, event-station matrix, signed decision record.

### 0.4 Paper 3 data Go/No-Go

Owner: Codex/research team for benchmark and reproducible engineering; PI for any
simulator license, author request, restricted waveform agreement, or institutional
data term.

- [ ] Inventory stations in South China, Hong Kong, Taiwan, Philippines, Vietnam, and surrounding networks. (The live EarthScope holdings query yields 145 three-component epochs and 75 unique network/station pairs; other FDSN centres, coverage gaps and ownership completeness remain.)
- [ ] Distinguish archived, downloadable, real-time-capable, restricted, and unavailable stations. (EarthScope archive extents exist for 8/10 response-priority pairs and six have samples within seven days; BAG/TWKB are absent from these holdings. Actual download, other centres, restrictions and SeedLink realtime/latency remain.)
- [ ] Verify waveform epochs, sample rates, three-component channels, responses, and licenses. (Ten geographic-priority station pairs now have checksummed StationXML with exact three-component response-stage/transfer-function structure; waveform holdings, epoch-matched deconvolution, latency and network terms remain.)
- [ ] Define noise-window strata: season, day/night, calm sea, typhoon, urban/remote, outages.
- [ ] Select a published PEGS waveform benchmark and obtain a validated simulator.
- [ ] Separately record whether a runnable implementation is public, licensed,
  author-provided, or must be independently reproduced; a method paper is not itself
  evidence of executable simulator access.
- [ ] Freeze the realistic station list before network experiments.
- [ ] Record a formal go, conditional-go, or no-go decision by the end of Week 2.

Immediate benchmark triggers:

- 2026-07-19 (Day 7): select the published event, stations, components, source model,
  Earth model, units, sampling, passband, and predeclared tolerances.
- 2026-07-26 (Day 14): record the QSSP-PEGS/normal-mode acquisition route and any
  author, license, or implementation dependency.
- 2026-08-09 (Day 28): reproduce the reference waveform within the frozen tolerances
  or issue a discrepancy report and activate the alternative validated route.
- 2026-08-23 (end Week 6): require at least one permitted continuous-noise pilot with
  response, timing, gaps, and provenance; metadata-only inventory is insufficient.

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
- [x] Integrate a mature elastic-load Green-function dataset or library. (LoadDef v1.2.2 exact tag/archive, isolated installation, PREM execution, `gE`/`gN` equation audit and normalization adapter are complete. Paper 1 CE angle/radial-displacement/`gE` fields match all 50 published Martens et al. 2019 rows exactly; broader tilt/strain discrepancies remain explicitly outside the authorized scope.)
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
- [x] Freeze gravity-gradient work as a validated supplemental foundation. (Route A
  does not require a gravity-gradient detectability result; legacy atom-gradiometer
  and GOCE anchors and P1-E003 remain reproducibility artifacts/future work.)
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
- [x] Freeze realistic parameter priors and citations for every process. (All six families now have evidence-linked `sensitivity_design_not_probability` joint designs with explicit model variants, coupling constraints, sample counts and deterministic seeds. The strict design audit reports 6/6 ready; this authorizes implementation/production execution but does not relabel named events or catalogue means as probability priors.)
- [ ] Run Latin-hypercube or Monte Carlo uncertainty with deterministic seeds. (Validated deterministic linear/log Latin-hypercube and quantile engine complete; cited priors, correlations, convergence and production ensembles remain.)

Foundation milestone: registered experiment `P1-E001-foundation` runs all six direct-gravity primitives under explicitly non-scientific engineering fixture parameters; it is infrastructure evidence, not an atlas result.

Coverage milestone: registered experiment `P1-E002-detectability-foundation` applies the 90% energy-coverage gate to three vertical-gravity literature anchors. It classifies only the engineering landslide/iGrav pair; all long-period processes remain unknown/partial rather than extrapolated.

Production primary-branch milestone: registered experiment `P1-E006-evidence-bounded-atlas` evaluates 1,446 evidence-bounded process--distance--parameter records on spherical/coastal or case-specific geometry. All six process families remain frequency-coverage-limited under the three admitted vertical-gravity literature anchors; no curve is extrapolated and no partial-band record is labelled detectable or undetectable. Structural model variants listed in the experiment disposition remain to be completed before the final sensitivity panel.

Figure milestone: the deterministic `P1-E006` production bundle renders and visually audits frequency support, spherical distance--amplitude envelopes, the process--instrument coverage matrix and non-probabilistic sensitivity envelopes. These are review-ready primary-branch assets; structural-variant closure still precedes final manuscript-asset status.

Reproduction milestone: registered workflows reproduce `P1-E005` and `P1-E006` byte-for-byte on AutoDL; the figure bundle is checksum deterministic and the eight-page results draft builds with no unresolved references/citations. The published-case submission exception gate passes on the open Helgoland model case while prohibiting unavailable Helgoland/Haikou observation statistics.

Structural-closure milestone: registered experiment `P1-E007-structural-variant-closure` implements the evidence-supported energy-normalized tsunami mapping and explicitly excludes underdetermined eddy, internal-wave and landslide branches instead of inventing surrogate parameters. This closes the primary model-form disposition gate; excluded variants remain documented future evidence needs, not zero-effect assumptions.

Scope-reconciliation milestone: Paper 1 route A is selected. Final closure is an evidence-bounded framework/frequency-coverage-limit paper, not a completed decision-grade detectability atlas. Title/claim alignment, direct-versus-total observable audit, systematic related work, scenario-family accounting, revised figures and independent geodesy review remain P0 submission gates.

Gradient coverage milestone: registered experiment `P1-E003-gradient-detectability-foundation` applies the same gate to all six `Tzz` fixtures and only the two gradient-instrument anchors; vertical-gravity curves are explicitly excluded.

Evidence: process configs, prior table, unit/physics tests, compact ensemble metrics.

### 1.5 Published-case reproduction

- [ ] Reproduce Helgoland storm-surge gravity magnitude and deformation components. (Event/month targets, exact processing contract, input manifest and executable pending/pass/fail audit are frozen. HELBH raw water level, both BSH-HBMnoku SSH grids, and HELG/HEL2 raw RINEX are acquired and integrity-checked on AutoDL. The 242-file BSH structural/time audit passes after two truncated race artifacts were detected and replaced. IGETS gravity still requires registered access, and the cited public GFZ processed GNSS dataset ends in 2021 rather than covering the 2022 event.)
- [ ] Quantify differences caused by geometry, resolution, Green functions, or domain truncation.
- [ ] Reproduce the Haikou NTOL magnitude/correlation only with legally available data or author-provided aggregates. (VOR—not preprint—targets, method contract, restricted/open input split and executable audit are frozen; SG/GNSS are author-restricted and exact CMEMS/MPIOM artifacts remain.)
- [ ] Record whether each case closes within 20–30% or supply a tested discrepancy explanation.
- [ ] Freeze compact regression fixtures from reviewed reproductions.

Evidence: reproducible case configs, metrics, plots, discrepancy report.

### 1.6 Atlas and Paper 1

- [ ] Produce process spectral-energy and cumulative-energy panels. (Route A
  replacement for the legacy frequency--equivalent-gravity deliverable.)
- [x] Cancel the distance--SNR panel for Route A. No SNR is authorized when the
  public noise evidence fails the spectral-coverage gate; distance--amplitude is
  retained instead.
- [x] Produce process–instrument detectability matrix. (`P1-E006` yields a complete coverage-gated matrix: all primary-branch records are unclassified because no admitted curve reaches 90% signal-energy coverage.)
- [x] Implement a frequency-coverage gate that forbids detectability classification when a curve covers less than the required signal-energy fraction.
- [x] Quantify the minimum low-frequency support required at 50%, 75%, 90% and
  95% spectral-energy coverage. (`P1-E008` reconstructs all 1,446 P1-E006
  records and reports intrinsic and instrument-bounded lower-edge requirements.)
- [ ] Produce a physical-structure and mass-compensation sensitivity panel.
- [x] Cancel universal detectable/boundary/undetectable classification for Route A.
  Classification remains withheld where frequency coverage is insufficient.
- [ ] Run Route-A sensitivity to process structure, geometry and coverage threshold.
  PSD, integration-time and detection-threshold SNR studies move to future work
  unless decision-grade site noise becomes available.
- [x] Move gravity-gradient detectability to the supplement/future-work boundary;
  it is not a Paper 1 release gate.
- [ ] Generate all manuscript figures and tables from one registered workflow.
- [x] Draft methods, results, limitations, data/code statements, and claim-safe abstract/title. (The eight-page registered-results PDF builds cleanly on AutoDL; author metadata, structural variants and journal formatting remain release gates.)
- [x] Complete internal reproducibility review and freeze Paper 1 release candidate. (G8 is a disclosed, user-authorized AI scientific audit rather than human peer review; G9 passed on AutoDL and repository release `paper1-v1.0.0` is frozen.)

Release-candidate convergence: RC01 scope governance, RC02 frequency
requirements, RC03 structured literature and RC04 observable-ledger audits pass.
The remaining P0 gates are the conceptual/final figure reorganization, explicit
Helgoland discrepancy decomposition, independent gravimetry/geodesy review,
single-command manuscript reproduction and archival submission package.

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

Non-restricted integration milestone: registered experiment `P2-E001-nonrestricted-readiness` connects the 17 completed method artifacts, 48-event open IBTrACS inventory, event-data gate, effect-ownership ledger and claim-safe decision audit. The method gate passes while real attribution correctly remains pending; this is not SG event evidence.

## Phase 3 — Paper 3 regional PEGS warning value (Weeks 16–24; benchmark starts Day 0)

### 3.1 Benchmark and Manila scenario library

- [ ] Complete the Day 0--28 published-event benchmark gate before regional scenario
  generation; this item is scheduled in Phase 0 even though its evidence is consumed here.
- [ ] Reproduce a published PEGS event at specified stations/components.
- [ ] Achieve waveform correlation >0.95, amplitude error <10–20%, and onset error below one sample, or document justified revised tolerances.
- [ ] Extract published Manila source segments, geometry, slip, and location-specific tsunami-arrival distributions. (Open Zhao/Niu source families and generation contract plus 19 Liu et al. PMEL scenario-family geometries/slips and five-location arrival ranges are extracted. No PEGS-ready record is registered because rise time, rupture velocity and explicit arrival-threshold definitions remain missing.)
- [ ] Record source-paper assumptions and avoid treating one 2.6-hour arrival as universal.
- [ ] Build 500–1000 baseline scenarios across Mw 8.0–9.0, segments, velocity, rise time, depth, dip, and heterogeneous slip.
- [ ] Preserve an interface for external tsunami calculations without claiming COMCOT simulation novelty.

Evidence: benchmark report, frozen scenario schema/table, simulator provenance.

### 3.2 Real station network and noise library

- [ ] Download permitted station metadata, responses, and waveform windows through manifests/scripts.
- [ ] Remove response and normalize components with timing checks.
- [ ] Label day/night, season, sea state, typhoon, urban/remote, gaps, and outages.
- [ ] Quantify PSD distributions, nonstationarity, transients, and cross-station correlation. (A provenance-preserving complete-case cross-station covariance estimator with explicit diagonal shrinkage and positive-definite gate is complete; real stratified PSD/covariance distributions, temporal colour and transient audits remain.)
- [ ] Freeze training, validation, held-out dates, held-out segments, and domain-out events before modelling.
- [x] Define existing, idealized, and incrementally augmented network variants. (`P3-E002` freezes a five-station exact response/archive-matched LH evaluation network, historical-only and excluded stations, 0/20/40% outage sets and augmented geographic roles. It is an archive design, not an operational network claim.)

Evidence: station/noise manifests, QC report, immutable split definitions.

### 3.3 Physics and statistical baselines

- [ ] Implement single-station amplitude/energy threshold baseline. (A mask-preserving sliding-RMS baseline freezes its threshold on calibration quiet windows and reports held-out quiet FAR, within-event trigger fraction and earliest triggering score index without mislabelling either as detection probability; response-corrected real waveforms, ensemble detection probability and passband evaluation remain.)
- [ ] Implement multi-station coherent stacking/template/likelihood baseline. (Aligned stacking, an independent-noise template statistic and a positive-definite cross-station covariance statistic are complete with mandatory timing/calibration provenance. Validated PEGS templates, temporal colour/nonstationarity, real covariance and likelihood comparisons remain.)
- [ ] Implement rapid source-parameter inversion for magnitude, region, and rupture segment. (A timing/provenance-aware discrete template-library inversion reports library-resolution Mw/segment, null-model improvement, second-best separation and explicit tied-best ambiguity under an independent-noise reference. Validated PEGS templates, confidence calibration, continuous/source-uncertainty inference and real covariance remain.)
- [ ] Calibrate thresholds to false alarms per month/year using long real-noise windows.
- [ ] Generate time-dependent detection probability and reliable-magnitude timelines. (Held-out detection/magnitude evaluators and a provenance-preserving discrete source-library prefix trajectory are complete; validated real-event trajectories, calibrated intervals and frozen reliability gates remain.)
- [ ] Evaluate vertical-only versus three-component data.
- [ ] Evaluate 0%, 20%, and 40% station outage.
- [ ] Determine the physical detectability boundary before any GNN training.

Evidence: baseline metrics, calibration curves, boundary/negative-result report.

Foundation milestone: registered experiment `P3-E001-physical-baseline-foundation`
connects the single-station threshold, two-station template and discrete source
inversion APIs. It deliberately fails the one-per-month false-alarm exposure gate
and is engineering infrastructure, not Manila PEGS detectability evidence.

Archive-network milestone: registered experiment `P3-E002-archive-network-design` exact-matches open LH archive triplets to response epochs for five stations and freezes 0/20/40% outage combinations. This authorizes predeclared real-noise downloads but does not pass the latency, waveform-QC or PEGS-template gates.

Open-waveform milestone: 22/25 predeclared original/replacement six-hour requests were retrieved and 21 passed response QC. Two five-station windows are structurally complete, but labels, false-alarm exposure and network-specific citation review remain pending; no threshold or PEGS claim is authorized.

Open-source milestone: Zhao and Niu (2025) supplies southern Mw 8.1 and northern Mw 9.1 recurrence-family anchors plus a Slab2-based generation contract. The released hazard dataset lacks per-scenario rise time, rupture velocity, full geometry and arrivals, so zero PEGS-ready Manila scenarios remain registered.

Open-noise pilot milestone: 22 of 25 frozen/replacement MiniSEED requests and 21 response-QC records succeed across five stations. Two complete five-station windows provide descriptive 0.005--0.05 Hz acceleration ASD and cross-station correlation, but all environment labels remain unclassified and threshold calibration is prohibited pending earthquake/weather/transient review.

### 3.4 Network optimization

- [x] Define objective combining detection time, probability, false alarms, magnitude error, and station cost/count. (A deterministic non-dominated Pareto frontier is implemented; policy weights are deliberately not hidden in a scalar score.)
- [ ] Evaluate station-count/performance curves for existing and augmented networks.
- [ ] Identify robust station locations under rupture and noise uncertainty.
- [ ] Quantify minimum instrument/noise requirements by magnitude and segment.
- [ ] Test network recommendations against outages and high microseism/typhoon noise.

Evidence: Pareto curves, recommended network, uncertainty and robustness report.

### 3.5 GNN conditional stage

- [ ] Start only if the published-waveform simulator benchmark passes and real-noise
  multi-station baselines show stable information at a predeclared false-alarm target.
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

1. Continue the Paper 1 Green-function, published-case, priors, SNR, and atlas sprint.
2. PI: register IGETS and send the approved Haikou/Wuhan access requests; Codex:
   inventory only actually deposited stations/products and audit channel closure.
3. Freeze and execute the published PEGS benchmark while separately resolving
   simulator source/license access and continuous real-noise access.
4. Push/backup compact repository artifacts and complete AutoDL cross-machine
   regression without counting those operations as a scientific gate.
5. Keep regional PEGS scenario expansion and all GNN training blocked until their
   explicit predecessor gates pass.
