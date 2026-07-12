# Literature and novelty evidence matrix

Audit date: 2026-07-12  
Scope: highest-risk nearest prior work for Papers 1–3  
Rule: facts below are separated into verified evidence, inference, and unresolved checks

This is a living audit, not a complete systematic review. Primary articles and official repositories are preferred. Search snippets are not sufficient for a manuscript claim; version-of-record (VOR) text, supplements, code, and data statements must be checked before submission.

## Paper 2: Haikou iGrav-048 South China Sea NTOL

**Source**

- Zhang et al. (2026), *The Influence of Non-tidal Ocean Loading in the South China Sea on iGrav-048 Superconducting Gravimeter Observations at the Haikou Station*, *Pure and Applied Geophysics*. DOI: [10.1007/s00024-026-03930-3](https://doi.org/10.1007/s00024-026-03930-3).
- VOR published online 2026-02-07; Crossmark reports the document current as of this audit.
- Accessible preprint: Research Square DOI [10.21203/rs.3.rs-7592512/v1](https://doi.org/10.21203/rs.3.rs-7592512/v1), posted 2025-10-10 under CC BY 4.0.

**Verified study design**

- Uses continuous iGrav-048 observations and CMEMS sea-surface height with load Green-function convolution; compares with MPIOM/GFZ predictions.
- Observation window is 2023-12-22 through 2024-04-30, deliberately chosen in Haikou's dry season to reduce hydrological contamination.
- Gravity preprocessing proceeds from one-second data to one minute and finally hourly observations, correcting gaps/steps/spikes, solid Earth tides, ocean-tide loading, atmosphere, and polar motion; rainfall and groundwater are modelled separately.
- The VOR explicitly treats the elastic loading contribution and additional direct Newtonian attraction. Therefore component separation is prior art and is not independently sufficient novelty for Paper 2.
- The analysed record is a continuous seasonal window rather than a named typhoon-event catalogue. No event-specific typhoon analysis was found in the available full-text search; the selected dry-season design intentionally reduces the rainy/typhoon-season hydrological complication.
- The paper compares CMEMS and MPIOM and separates contributing sea regions. This raises the standard for “multi-model validation” and “regional contribution” claims.

**Version discrepancy that must not be mixed**

- The accessible 2025 preprint abstract reports CMEMS correlation approximately 0.8, about 40% explained residual signal, and maximum CMEMS gravity change 1.8 microgal.
- VOR indexing/author-provided preview reports a maximum CMEMS gravity change of 2.6 microgal and correlations greater than 0.8. The precise VOR coefficient must be transcribed from the final PDF/table before any quantitative reproduction target is frozen.
- Reproduction must cite and match the VOR inputs, equations, revisions, and date range; a preprint/VOR hybrid target is invalid.

**Implication for Paper 2**

Paper 2 needs a joint package: named typhoon-event attribution, atmospheric/hydrological/ocean closure under severe weather, independent tide-gauge/GNSS/track evidence, quiet controls, and held-out-event or cross-station performance. “Direct versus elastic separation” is required physical hygiene but no longer a standalone novelty claim.

**Unresolved**

- Obtain the definitive VOR PDF and any supplements; record exact correlation(s), 2.6-microgal definition (range, peak, or peak-to-peak), final equations, product identifiers, and revisions.
- Determine whether later dates after the 2024 outage include typhoons but were excluded from the main analysis.
- Determine whether raw/near-raw iGrav-048, pressure, maintenance, calibration, rainfall, and groundwater records can be shared.

## Paper 2 benchmark: Helgoland NTOL and storm surges

**Sources**

- Voigt et al. (2024), *Non-Tidal Ocean Loading Signals of the North and Baltic Sea From Terrestrial Gravimetry, GNSS, and High-Resolution Modeling*, *Geophysical Research Letters* 51, e2024GL109262. DOI: [10.1029/2024GL109262](https://doi.org/10.1029/2024GL109262).
- Helgoland station/data DOI landing pages are linked from the official [IGETS database](https://isdc.gfz.de/igets-data-base/).

**Verified benchmark facts**

- Uses high-resolution regional BSH-HBMnoku ocean modelling with SG, GNSS, and tide-gauge observations; compares regional predictions with global products.
- For the 2022-01-30 storm-surge maximum, reports up to 85 nm/s2 peak-to-peak gravity increase, -34 mm vertical displacement, and +2.0 m sea level above mean high water at Helgoland.
- Reports Helgoland correlations of 0.87 (gravity) and 0.74 (GNSS) with the BSH model, and 50% gravity-residual signal reduction in the highlighted storm period.
- Multiple storm surges and additional continental SG stations are included; Paper 2 cannot present “multi-event NTOL” alone as novel.

**Implication**

Helgoland is the open methodological benchmark. Paper 2 must distinguish tropical-cyclone event physics, confounder closure, regional model limitations, and held-out generalization rather than repeat a storm-window correlation study.

## Paper 3: PEGSGraph

**Source**

- Hourcade, Juhel & Bletery (2025), *PEGSGraph: A Graph Neural Network for Fast Earthquake Characterization Based on Prompt ElastoGravity Signals*, *JGR: Machine Learning and Computation* 2, e2024JH000360. DOI: [10.1029/2024JH000360](https://doi.org/10.1029/2024JH000360).
- Official code linked by the paper: [gitlab.com/kjuhel/pegsgraph](https://gitlab.com/kjuhel/pegsgraph), GPL-3.0-or-later, with tagged releases visible at audit time.

**Verified study design**

- PEGS Green functions are computed in AK135 with QSSP; source-time functions cover mechanism-dependent magnitude ranges and are perturbed for duration/shape variation.
- Synthetic PEGS are combined with simultaneous empirical broadband-station noise windows, preserving network-scale noise correlation.
- Vertical records are response-corrected, detrended, band-passed 2–30 mHz, and decimated to 1 Hz; sensors with annual median hourly standard deviation above 1 nm/s2 are excluded.
- The graph uses stations as nodes and geographic k-nearest-neighbour edges (`k=18` in the described model), predicting magnitude, location, and moment-tensor parameters.
- The work already addresses network geometry, empirical noise, and sensor-input flexibility. Paper 3 cannot claim those concepts generically.

**Implication**

Paper 3 must use identical splits/false-alarm constraints when comparing a GNN with physical baselines, explicitly test South China regional geometry, station availability, typhoon/microseism strata, unseen rupture segments/dates, outages, and calibration.

## Paper 3: Peru monitoring-system implementation

**Source**

- Arias et al. (2026 issue / accepted 2025), *First implementation of a tsunami warning system based on prompt elastogravity signals in Peru*, *Geophysical Journal International* 244, ggaf419. DOI/article: [GJI ggaf419](https://academic.oup.com/gji/article/244/1/ggaf419/8300379).

**Verified system and performance facts**

- Implements PEGSGraph within the Instituto Geofísico del Perú real-time monitoring workflow using 95 broadband stations from Peru and surrounding countries.
- Earthworm performs acquisition; stations with latency above about 120 s may be considered offline. A P-wave STA/LTA workflow triggers PEGSGraph after at least 30 stations detect an event.
- Preprocessing removes response, demeans/detrends, converts to acceleration, filters 2–30 mHz, decimates to 1 Hz, zeros traces after estimated P arrival, and clips at 10 nm/s2.
- Reported operational evaluation is a simulated real-time test: recorded waveforms/noise from the 2024 Mw 7.2 Arequipa event augmented with synthetic Mw 8.2–9.5 PEGS. No recent real Mw >=8.2 event was available for end-to-end validation.
- The paper reports sufficient magnitude estimates for Mw >=8.2 within about 5 min in aggregate, but performance is strongly source/noise dependent. At 300 s, success for Mw 8.2 across six high-risk portions ranges from 23.4% to 61.7%; the noisiest quartile has lower accuracy than the quietest.
- The paper discusses a no-PEGS control and magnitude-estimation success, but a manuscript-wide search found no explicit “false alarm” metric expressed as false triggers per month/year. Paper 3 should treat this as a key evaluation gap, subject to full supplement/code confirmation.

**Implication**

“PEGS before tsunami arrival” and “PEGS real-time system” are occupied claims. The defensible increment is a South China/Manila decision study with realistic continuously sampled noise, explicit alert false-alarm rate, comparison with regional P/W-phase/GNSS timelines, station outages/latency, network optimization, and scenario-specific tsunami-arrival distributions.

## Data-access facts

The official IGETS database states that it hosts worldwide SG products with:

- Level 1 raw gravity and local pressure at 1–2 s plus one-minute decimations;
- Level 2 gravity/pressure corrected for instrumental perturbations;
- Level 3 residuals after specified geophysical corrections.

Access is password protected and requires user registration. The station table (last modification 2026-01-13) lists Helgoland iGrav-047 from 2020 and Wuhan instruments through the listed epochs, but does not list Haikou iGrav-048. Therefore Helgoland is a concrete registered-access benchmark; Haikou requires direct author/station coordination and must not be assumed downloadable from IGETS.

## Claim changes caused by this audit

1. Paper 2: direct/elastic component separation is mandatory but already demonstrated at Haikou; novelty must rest on event attribution plus severe-weather closure and generalization.
2. Paper 2: model-to-model comparison and regional contribution analysis are also prior art.
3. Paper 3: empirical correlated noise, network geometry, station outages as an architectural concern, and operational integration are prior art.
4. Paper 3: explicit continuous-stream false alarms, South China domain shift, typhoon/microseism noise, regional baseline comparisons, and optimized station requirements remain the sharper target.

