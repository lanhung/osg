# Papers 2 and 3 completion plan after IGETS account creation

Audit date: 2026-07-14

This plan treats the principal investigator's IGETS account as created but does
not treat login, station coverage, file rights, or data delivery as verified.
Haikou iGrav-048 is an optional collaboration dataset, not a critical-path
dependency. The plan assumes that it may never become available.

## Executive decision

Paper 2 can now move from method readiness to a real-data acquisition gate. Its
primary route is a station-neutral IGETS study: first inventory authenticated
Level 1 holdings, then freeze the strongest typhoon-exposed station/event design
that satisfies complete gravity, pressure, calibration and station-log
provenance. Hsinchu, Wuhan and Matsushiro are public-table inquiry candidates,
not preselected study stations. Haikou may later be an external validation site.

Paper 3 does not depend on IGETS or Haikou. Its immediate critical path is (1)
environmentally labelled continuous regional seismic noise, (2) continuous-flow
false-alarm exposure, and (3) one independently validated PEGS waveform
benchmark. Until the benchmark passes, Manila detectability, warning time and
GNN results remain prohibited.

## Current evidence and completion estimates

| Workstream | Engineering readiness | Scientific-result readiness | Submission readiness |
| --- | ---: | ---: | ---: |
| Paper 2 | 70% | 20% | 30% |
| Paper 3 | 65% | 20% | 30% |

The estimates deliberately separate code from evidence. Paper 2 has a complete
component-ownership contract, an open 48-event IBTrACS inventory and evaluation
scaffolding, but no authorized real SG event. Paper 3 has a response-matched
five-station archive design, 35 response-QC station-days, physical baselines and
source-family extraction, but no environmentally approved threshold data and no
validated PEGS waveform.

## Paper 2: real-data route without Haikou

### Final scientific question

Can a named tropical cyclone's ocean mass redistribution be attributed in a
superconducting-gravimeter record after independently accounting for atmosphere,
hydrology, direct ocean attraction, elastic/potential loading, instrument
effects and severe-weather controls?

The claim is event attribution, not generic NTOL correction and not the first
typhoon observation. The minimum publishable design remains either one station
with at least three usable cyclone events or two stations with at least two
events each, including a held-out event and non-cyclone controls.

### Route ladder

| Route | Required evidence | Permitted paper scope | Status |
| --- | --- | --- | --- |
| P2-A | IGETS Level 1 SG + local pressure + calibration/logs at a typhoon-exposed station | Original named-typhoon attribution paper | Primary |
| P2-A+ | P2-A plus Haikou iGrav-048 | Cross-station South China Sea validation | Optional strengthening |
| P2-B | Equivalent tropical-cyclone station outside the original region | Tropical-cyclone attribution with revised geography | Accepted fallback |
| P2-C | Helgoland or another extratropical coastal SG with storm-surge closure | Storm-driven ocean-loading attribution; title and claims narrowed | Last scientific fallback |
| P2-D | No raw-enough SG | Methods/readiness report only | Not sufficient for the current paper claim |

Haikou loss therefore removes the strongest geographically aligned station but
does not invalidate Paper 2. Failure of every registered IGETS candidate to
provide raw-enough event windows would force P2-C or stop the paper, rather than
manufacture an attribution result.

### Acquisition gates

1. **Public inventory gate.** Snapshot the official IGETS station/sensor table,
   screen only for acquisition priority and record its checksum.
2. **Authenticated directory gate.** After interactive login, record exact
   station codes, levels, file years, remote paths and station-specific terms.
   Public station-table dates are not file coverage.
3. **Header-first gate.** Retrieve documentation, calibration and representative
   headers before bulk waveforms. Confirm units, sign, cadence, time standard,
   pressure channel, scale factor and pre-applied corrections.
4. **Event-coverage gate.** Cross-match actual files—not nominal sensor epochs—
   to IBTrACS. Freeze training, held-out, strong-weather and quiet windows before
   looking at gravity amplitudes.
5. **Closure gate.** Reject a station as the primary paper site if pressure,
   timing, discontinuity, calibration or correction provenance cannot be closed.
6. **Rights gate.** Keep restricted waveforms on AutoDL. Commit only queries,
   terms, checksums and compact non-identifying metrics permitted by the licence.

### Analysis work packages

| ID | Work package | Output and pass condition | Dependency |
| --- | --- | --- | --- |
| P2-01 | IGETS public and authenticated inventory | Exact station/level/year/path manifest | Account login |
| P2-02 | Station-event feasibility freeze | At least one design meeting the event-count gate | P2-01, IBTrACS |
| P2-03 | Raw SG/pressure QC | Units, cadence, gaps, jumps, calibration and timing pass | P2-02 |
| P2-04 | Independent corrections | Tides, polar motion, pressure, hydrology and drift retained as separate series | P2-03 |
| P2-05 | Ocean forward model | Direct and elastic/potential terms, component benchmark, coastal resolution convergence | CMEMS/ERA5 or equivalent |
| P2-06 | Severe-weather closure | No atmosphere-ocean double count; pressure, rain and sea-level diagnostics | P2-04/05 |
| P2-07 | Registered attribution | Held-out event, controls, uncertainty and failure retention | P2-06 |
| P2-08 | Cross-event/station sensitivity | Leave-one-event-out or cross-station generalization | P2-07 |
| P2-09 | Manuscript release | One-command compact reproduction; restricted-data instructions | P2-08 |

### Paper 2 timing

After authenticated access is provisioned on AutoDL, public/remote inventory and
one small pilot require about 2--4 working days. Event and control freeze plus
raw QC requires 1 week. Corrections and ocean forward modelling require 2--4
weeks, attribution and robustness 2--3 weeks, and manuscript/release work 2
weeks. A defensible submission is therefore approximately 7--10 focused weeks
after a usable station closes. Haikou collaboration may proceed in parallel and
must not reset this clock.

## Paper 3: work that remains independent of PEGS simulator access

### Work that can proceed now

1. Complete station-local weather, pressure, regional sea-state, microseism and
   waveform-transient labels for the frozen eight-day Stage 1 sample. A day may
   be retained as a named noisy stratum; it need not be discarded merely because
   an earthquake candidate exists.
2. Freeze a Stage 2 calendar/stratified sampling rule before inspecting waveform
   amplitudes. Obtain at least 32 accepted calibration days and 32 independent
   held-out days so the empirical false-alarm resolution is reportable.
3. Implement continuous-stream segmentation with dead time, overlapping-window
   accounting and event clustering. Report both raw threshold crossings and
   operational alert clusters per 30 days.
4. Audit station outages and correlated-noise covariance by season and condition;
   preserve the same simultaneous windows across stations.
5. Finish Manila source parameter provenance. Missing rise time and rupture
   velocity must be assigned only through a preregistered, cited uncertainty
   family, never silently filled with a point value.
6. Freeze a blind-injection interface. The evaluator receives waveform IDs and
   hidden source/noise labels; the simulator adapter can be added later without
   changing splits or metrics.
7. Finish conventional comparison contracts for P-trigger, W-phase, GNSS and
   site-specific tsunami arrival definitions. Literature timing is a benchmark,
   not a fabricated local observation.

### Work that remains blocked by the PEGS physics gate

- physical signal amplitude and waveform at regional stations;
- detection probability versus time at fixed false-alarm rate;
- reliable magnitude time and Manila warning lead;
- station placement optimization conditioned on PEGS information;
- any GNN training or comparison.

### Paper 3 route ladder

| Route | Required evidence | Output |
| --- | --- | --- |
| P3-A | QSSP-PEGS or published normal-mode benchmark passes | Full Manila detectability and warning-value paper |
| P3-B | Independently implemented solver passes two published/analytic cross-checks | Full paper with stronger method-validation section |
| P3-C | No simulator, but >=64 accepted real-noise days and continuous false-alarm analysis | Regional network/noise requirements and feasibility-boundary paper; no Manila detectability claim |
| P3-D | Neither simulator nor sufficient continuous noise | Technical report only; current paper cannot be submitted |

### Paper 3 release gates

| Gate | Pass condition |
| --- | --- |
| Noise provenance | Exact channels, responses, time epochs, gaps, licence and checksums |
| Environmental labels | Earthquake, cyclone, local weather/pressure, sea state and transient/microseism layers complete |
| Exposure | >=32 accepted days in each independent split or an explicit weaker false-alarm resolution |
| Simulator | Published waveform correlation >0.95, amplitude error within preregistered 10--20%, onset within one sample or justified |
| Scenarios | Dynamic Manila parameters and arrival definitions complete with uncertainty families |
| Baselines | Energy, coherent/template and covariance methods evaluated before GNN |
| Evaluation | Held-out rupture segments and noise dates; 0/20/40% fixed outage identities |
| Operations | Alert clusters per 30 days, latency/outage sensitivity, conventional timeline comparison |
| Release | Code/configs/compact metrics public; raw waveform and simulator rights respected |

### Paper 3 timing

Environmental Stage 1 closure and Stage 2 freeze require about 1--2 weeks.
Acquiring and QC'ing the 64-day minimum is primarily I/O and should take 1--2
weeks once product sources are fixed. Continuous false-alarm and covariance
baselines require 2--3 weeks. A validated simulator plus scenario production and
blind evaluation require another 4--7 weeks. The full P3-A/P3-B route is roughly
10--14 focused weeks; the P3-C requirements-boundary fallback is roughly 5--8
weeks and must use a different title and claim.

## Immediate execution order

1. Run the new public IGETS inventory and typhoon-overlap screening on AutoDL.
2. Have the PI perform one interactive authenticated IGETS login on AutoDL; then
   inventory remote directories and retrieve headers/calibration only.
3. Freeze P2 station/event candidates from actual file coverage before bulk SG
   download.
4. In parallel, register Paper 3 environmental-label completion and continuous
   false-alarm exposure; do not start GNN work.
5. Close or formally downgrade the PEGS simulator route by the benchmark gate;
   do not allow indefinite access waiting to stall the noise-boundary paper.

## Credential and storage boundary

No IGETS username, password, token, private key or restricted waveform enters
Git. Data-user SFTP currently requires interactive/password-backed access; the
PI should establish the session or an owner-only rclone configuration directly
on AutoDL. Codex can then inspect directories and process files without ever
receiving the password in chat. Large data remain under
`/root/autodl-tmp/ocean-gravity-run/data/raw/`; local Git receives code,
manifests, documentation and compact permitted results only.
