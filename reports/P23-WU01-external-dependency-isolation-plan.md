# P2/P3 external-dependency isolation and execution plan

Date: 2026-07-12

## Dependency boundary

| Workstream | IGETS / Haikou | PEGS simulator | Current action |
|---|---:|---:|---|
| Paper 2 SG event attribution, calibration/log review and held-out event metrics | required | no | blocked; preserve real-data gate |
| Paper 2 open storm catalogue and processing/evaluation contracts | no | no | complete and register readiness audit |
| Paper 2 CMEMS/ERA5 inverse-barometer ownership | no | no | independent blocker; exact product semantics still required |
| Paper 3 Manila source/arrival literature table | no | no | extract and freeze before scenario generation |
| Paper 3 station metadata, response, archive and real-noise library | no | no | freeze archive network, then download small registered windows |
| Paper 3 threshold, covariance, outage and network-design APIs | no | no | complete engineering/statistical baselines without detectability claims |
| Paper 3 published PEGS benchmark and physical detectability boundary | no | required | blocked pending licensed simulator/validated waveforms |
| Paper 3 GNN and warning-value claims | no | required plus real-noise gate | prohibited until both predecessor gates pass |

## Execution order

1. Register `P2-E001` to combine the open IBTrACS inventory, method artifacts,
   event-data gate, effect-ownership gate and claim-safe decision gate. A pass
   means only that all non-restricted method work is connected and that missing
   observations remain correctly pending.
2. Register `P3-E002` to select only stations with open three-component LH
   archives and complete response structure, freeze 0/20/40% outage variants,
   and retain historical/metadata-only stations separately.
3. Use the selected `P3-E002` network for small, predeclared waveform windows.
   Store raw MiniSEED and StationXML only on AutoDL; commit queries, hashes,
   response-removal/QC metrics and split roles.
4. Extract numeric Manila parameters from primary sources. Missing rise time,
   rupture velocity or location-specific arrival remains missing rather than
   receiving a default value.
5. Update both methods-first manuscripts and route every result-dependent figure
   through its predecessor gate. No synthetic fixture enters a Results section.

## Stop conditions

- Paper 2 does not select a pilot event from storm proximity alone.
- Paper 3 does not call an archive station operational or real-time-capable.
- No PEGS detection probability, magnitude accuracy or warning lead time is
  reported without the published-waveform simulator benchmark.
- GNN work remains off until validated PEGS templates and real-noise baselines
  both show stable information at the frozen false-alarm target.
