# P1-WU59 HELBH tide-gauge acquisition

Status: complete for source acquisition and integrity; scientific preprocessing
and local-attraction calibration remain pending.

The official PEGELONLINE station record identifies `HELGOLAND BINNENHAFEN`
(station number `9510070`, UUID
`c0ec139b-13b4-4f86-bee3-06665ad81a40`). The selected product is
`WASSERSTAND ROHDATEN`; its PNP offset is −5.015 m in DHHN2016, valid from
2019-11-01. The exact query and usage terms were frozen in the input manifest
before download.

The official endpoint was submitted with the registered UTC bounds
`2022-01-26T00:00:00Z` and `2022-02-25T00:00:00Z`. PEGELONLINE returned an
archive containing the JSON series, the usage-terms pointer, and series
metadata. Source timestamps use the legally applicable local UTC offset; the
first and last timestamps are respectively `2022-01-26T01:00:00+01:00` and
`2022-02-25T01:00:00+01:00`, exactly matching the registered UTC bounds.

Integrity and structural checks on AutoDL:

- ZIP test: pass, three members;
- archive SHA-256:
  `93a1fb84b23d531321b48a16a3cf121976837e500380e7ebaf1c82379da0e3c9`;
- embedded JSON SHA-256:
  `b213996bf38e497ffea06690d22845ce32a3f55893159bfdfddb4d2a6fd7c7b1`;
- 43,201 records, inclusive endpoints, exact 60-second cadence;
- zero missing timestamps and zero null values;
- unit `cm`, range 326–805 cm;
- source quality flag `unchecked`.

The archive remains only on AutoDL at the path recorded in
`data/manifests/helgoland_reproduction_inputs.json`; code, configuration,
checksums, and this compact audit remain local. No gravity, deformation,
correlation, or RMS-reduction target is marked reproduced by this acquisition.
