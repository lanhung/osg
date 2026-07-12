# P1-WU39 process-parameter evidence ledger, first pass

Status: tide, storm-surge benchmark and mesoscale-eddy anchors encoded; three
process families remain intentionally unresolved

## Encoded anchors

- M2 astronomical period: 12.4206012 h = 44,714.16432 s (NOAA tide
  documentation).
- Helgoland 2022-01-30 benchmark: +2.0 m above mean high water, 85 nm/s²
  peak-to-peak gravity, and −34 mm vertical displacement (Voigt et al. 2024,
  DOI `10.1029/2024GL109262`).
- Global tracked mesoscale-eddy means: 8 cm SSH amplitude and 90 km
  speed-based radius (Chelton et al. 2011, DOI
  `10.1016/j.pocean.2011.01.002`).

None is labelled a probability prior: the tide period is a constant, Helgoland
is one event, and the eddy values are catalogue means without an encoded
distribution. The eddy source also cautions that the chosen Gaussian profile is
not necessarily the best composite profile, so profile sensitivity is required.

## Foundation comparison

The frozen engineering tide period differs slightly from the astronomical
value; it remains unchanged to preserve registered checksums. The engineering
eddy amplitude (0.3 m) is well above the cited 0.08 m global mean, and its 50 km
Gaussian scale is not definitionally interchangeable with the 90 km speed-based
radius. This confirms why `P1-E001`–`E004` cannot be promoted to paper results.

## Remaining gate

Internal-wave, earthquake-tsunami and submarine-landslide parameter families
remain excluded from a scientific ensemble until mode/source-specific evidence
and range semantics are encoded. Negative or incomplete evidence is retained
rather than filled with uncited convenient ranges.
