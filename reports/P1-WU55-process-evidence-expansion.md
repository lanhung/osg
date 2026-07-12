# P1-WU55 internal-wave, tsunami and landslide evidence anchors

Status: named evidence anchors added; production probability priors remain
deliberately disabled.

New traceable anchors include:

- northern South China Sea internal-tide/solitary-wave isopycnal displacements
  around 100/150 m, one 240 m extreme observation, and globally mapped mode-1 M2
  beam widths of 100–300 km;
- the 2011 Tohoku tsunami's DART-inferred 300–400 km by 100 km source and the
  2004 Sumatra event's greater-than-1 m mid-ocean peak-to-trough satellite
  observation; and
- Storegga volume 2400–3000 km³, reconstructed 450 km runout, 30–40 m/s frontal
  progression and a local modeled maximum near 60 m/s.

These values are not independent quantiles. In particular:

- an isopycnal displacement cannot determine gravity without stratification,
  mode shape, free-surface response and mass compensation;
- an earthquake source footprint, propagating open-ocean wave and coastal run-up
  are not the same amplitude/scale; and
- Storegga is a giant extreme whose volume, runout and maximum velocity cannot be
  sampled independently.

Accordingly every new evidence entry remains
`probability_prior_eligible: false`, and unresolved physics/data fields remain in
the manifest. The production Latin-hypercube gate must continue to reject these
processes until coherent scenario families—not arbitrary min/max combinations—
are frozen.
