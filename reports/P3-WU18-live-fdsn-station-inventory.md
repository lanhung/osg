# P3-WU18 live EarthScope FDSN station inventory

Status: live EarthScope channel inventory retrieved and summarized; waveform,
response, latency, licensing and non-EarthScope holdings remain unresolved.

The channel-level query covers 5–30 N, 100–130 E, BH?/LH?, and epochs
intersecting 2020-01-01 through 2026-07-12. The 65,280-byte response has
SHA-256 `12daf91de2aad1a12630da7eca6245f914f8173662b0e0170e99506ac2a4fdce`.
The raw response remains ignored by Git; the exact query and compact summary are
versioned.

The conservative exact-epoch parser found 145 three-component channel epochs,
14 incomplete epochs and 75 unique network/station pairs across 12 networks.
All 145 candidate epochs contain scalar sensitivity fields, but that does not
establish a complete poles/zeros response.

Of these, 81 three-component epochs across 46 unique network/station pairs have
an empty metadata end time. This is a reproducible inventory field, not an
operational claim: an open-ended epoch may still be offline, delayed, archival
only or absent from the EarthScope waveform holdings.

No station is yet labelled real-time-capable. The next audit must query response
metadata and waveform availability for frozen epochs, inspect terms and
acknowledgements, add other relevant FDSN centres, and distinguish archival,
downloadable, real-time, restricted and unavailable stations.
