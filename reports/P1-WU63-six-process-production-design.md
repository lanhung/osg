# P1-WU63 Six-process production sensitivity design

Status: prior/design gate pass (`6/6`); implementation and production execution
remain separate gates.

The six process families now have frozen, evidence-linked joint designs. Every
design uses `sensitivity_design_not_probability`; none of the named events,
catalogue means, selection thresholds, model ranges, or extreme observations is
reported as a probability distribution or percentile.

Key design decisions:

- tide and storm surge use the registered BSH-HBMnoku regional fields so spatial
  footprint, amplitude, phase, wet mask and duration remain coupled;
- the eddy branch compares catalogue-mean Gaussian, quadratic-composite and
  equal-positive-mass compensated structures without assigning model weights;
- the internal-wave branch derives density anomaly from displacement and a
  regional buoyancy-frequency reference, and separates coherent M2 and solitary
  extreme families;
- the tsunami branch separates amplitude-normalized and energy-normalized
  mass-balanced packets and uses wavefront distance;
- submarine landslides are stratified into regional-median, Storfjorden dynamic
  and Storegga giant families so extreme volume, runout and velocity are not
  recombined independently.

The readiness audit was extended to support evidence-backed constants in
addition to ranges. It checks units, finite constants/ranges, sampling semantics,
model variants, joint constraints, evidence references, sample count and seed.
`reports/process_prior_readiness.json` now records no blocker for any process.

Passing this gate authorizes implementation and registered production execution;
it does not assert that all listed model variants or instrument curves are
already complete.
