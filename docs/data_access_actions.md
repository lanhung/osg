# Data-access action pack

Audit date: 2026-07-14

These actions require a human identity, affiliation, acceptance of terms, CAPTCHA, or station-owner approval. Codex must prepare and track them but must not impersonate the principal investigator or claim that a request was sent.

Hard dates, owners, and fallback triggers are tracked in
`data/manifests/critical_path.yml`. An unchecked action below must not be described
as registered, requested, approved, or delivered without human-supplied evidence.

## Action A — IGETS user registration

Register at the official [IGETS data-user page](https://isdc.gfz.de/igets-data-base/registration-for-data-users/). The form requires personal/institutional information and a CAPTCHA.

PI-reported status on 2026-07-14: **account created; authenticated login and
station/file inventory not yet verified**. Account creation must not be
represented as delivery of Hsinchu, Wuhan, Helgoland or any other station data.

Current official access facts:

- download requires a registered account;
- transport is encrypted SFTP, not legacy FTP;
- current host is `igetsftp.gfz.de`;
- Level 1 includes raw gravity and local pressure at 1–2 s plus one-minute data;
- Helgoland Level 1 DOI is [10.5880/igets.he.l1.001](https://doi.org/10.5880/igets.he.l1.001).

After registration, record only the account existence and access date in the private operations log. Never commit username/password. Inventory directories and file headers before downloading bulk data, then create a manifest containing station, sensor, level, exact time range, remote paths, license/terms, and checksums.

For the first authenticated session, the PI should log in interactively from
AutoDL or create an owner-readable (`chmod 600`) rclone configuration there.
Do not paste the password into chat, a shell command, a Git-tracked file or a
process argument. Codex may continue after login by inventorying remote paths and
downloading header/calibration files before any waveform bulk transfer.

## Action B — Haikou iGrav-048 collaboration/data request

Status update on 2026-07-14: current policy changes make near-term delivery
unlikely. Communication may continue, but Paper 2 must be designed to succeed
without iGrav-048. Haikou is optional cross-station validation rather than the
primary data gate.

Send from the principal investigator's institutional address to the corresponding author/station contact shown in the VOR. Suggested English text:

> Subject: Research collaboration request on event-resolved typhoon ocean loading at Haikou iGrav-048
>
> Dear Dr. [name],
>
> We are developing an event-resolved study of typhoon-driven ocean mass redistribution in superconducting-gravimeter observations. We have read your 2026 *Pure and Applied Geophysics* study carefully and intend to build directly on—not duplicate—its South China Sea NTOL modelling framework.
>
> Our proposed increment is to analyse named typhoon events and close the gravity budget across direct ocean attraction, elastic response, atmosphere, hydrology, tide gauges/GNSS where available, and held-out events. We would like to ask whether collaboration and access could be considered for:
>
> 1. continuous iGrav-048 Level 1 or nearest-available gravity data covering at least three typhoons, preferably with seven days before and after each event;
> 2. colocated pressure, calibration factors/absolute-gravity comparisons, timing information, gap/step/jump/maintenance logs, and details of any pre-applied corrections;
> 3. rainfall and groundwater series used for hydrological correction;
> 4. information on post-September-2024 data continuity and candidate typhoon periods;
> 5. applicable data-use, co-authorship, acknowledgement, embargo, and redistribution conditions.
>
> We will not redistribute restricted observations and will provide the complete processing code, manifests, and event-level validation results to collaborators. We would be glad to share a short analysis protocol before any transfer.
>
> Sincerely,  
> [PI name, title, institution, ORCID, contact]

Do not send until PI identity, institution, intended collaborators, data-storage security, and authorship/data terms are approved.

## Action C — Helgoland benchmark

After IGETS access is active:

1. inventory `he047` Level 1 gravity and pressure for 2022-01-23 through 2022-02-14 (covering the highlighted 2022-01-30 event and surrounding surges);
2. retrieve calibration/header/documentation files before waveform data;
3. identify HELBH tide gauge, BSH-HBMnoku product access, and HELG/HEL2 GNSS sources and licenses;
4. reproduce the reported 85 nm/s2 peak-to-peak gravity, -34 mm displacement, 0.87 gravity correlation, and relevant residual reduction only under the paper's exact preprocessing;
5. keep VOR numbers distinct from outreach-page rounded values (“almost 90 nm/s2”).

## Action D — Paper 3 station inventory

The NSF SAGE station service moved in June 2026. Use the current endpoint:

```text
https://service.earthscope.org/fdsnws/station/1/query
```

Do not use removed `includeavailability` or `matchtimeseries` parameters. Station metadata and response availability are different from waveform availability; query them separately. Start with the versioned query in `data/manifests/paper3_fdsn_inventory.yml`, inspect channel epochs and responses, then query the availability service for frozen noise dates.

The initial geographic box is deliberately broad and not the final “realistic network.” A station enters the experimental network only after channel epoch, response, waveform availability, license, latency class, and noise QC are recorded.

## Action E — PEGS simulator and benchmark acquisition

This action starts immediately and is independent of Manila Trench station-data
authorization. Treat the following as separate deliverables:

1. freeze one published earthquake benchmark, source/Earth models, stations,
   components, sampling, passband, units, and tolerances;
2. determine whether the QSSP-PEGS or normal-mode implementation is publicly
   runnable, licensed, author-provided, or must be independently implemented;
3. have the PI make any required author/license request without claiming access in
   advance;
4. reproduce the published waveform and save correlation, amplitude, onset, and
   provenance evidence;
5. only after the benchmark passes, generate production Manila scenarios.

A methods paper does not by itself prove executable-code access. Station metadata
does not prove continuous waveform availability. Neither gap may be replaced with an
invented waveform or white-noise scientific experiment.
