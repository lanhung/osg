# P2-WU26 live IBTrACS candidate inventory

Status: official open track archive retrieved and broad regional candidates
frozen; SG coverage and station-distance ranking remain unresolved.

The NOAA/NCEI IBTrACS v04r01 last-three-years CSV was retrieved on
2026-07-12. The 9,434,011-byte payload has SHA-256
`91217d5c3caf56c02c858fc699ccac80c683ed14d50ab6495963470b964f9608`
and an HTTP Last-Modified value of 2026-07-09 09:13:04 GMT. The raw CSV and its
retrieval sidecar remain outside Git; their manifest and compact selection are
versioned.

The frozen 5–25 N, 100–125 E, western North Pacific rule yields 48 events from
2023 through the retrieval date. This is deliberately a broad inventory, not a
Paper 2 event catalogue. Candidate status does not establish iGrav-048 or any
other SG coverage, raw-enough product level, pressure/instrument logs, nearby
tide gauge/GNSS, or sufficient ocean-loading amplitude.

A second, explicitly non-scientific screening stage uses the Haikou city proxy
at 20.00 N, 110.34 E because the VOR does not publish a machine-readable exact
iGrav-048 coordinate. Requiring at least 80 kt regional USA wind and no more than
350 km closest approach yields 11 priority coverage inquiries. The proxy cannot
be used for gravity forward modelling.

The frozen priority names are Talim, Saola, Haikui and Koinu (2023); Yagi,
Yinxing, Toraji and Man-yi (2024); and Kajiki, Ragasa and Matmo (2025). Yagi is
closest to the proxy at about 14.6 km. This is not evidence that iGrav-048 was
operational during Yagi or any other event.

The next gate must replace the proxy with an author-confirmed instrument
coordinate and intersect these 11 events with actual SG, pressure, calibration,
maintenance, rainfall, tide-gauge and GNSS coverage before choosing the pilot and
train/held-out events.
