# Instrument performance evidence and modelling decisions

Audit date: 2026-07-12

The machine-readable curves are in `data/manifests/instrument_noise_curves.json`. They are literature anchors, not interchangeable “best sensitivity” curves. Each preserves observable, conditions, source-reported quantity, and any additional assumption used to form a two-node curve.

## iGrav superconducting gravimeter

Schäfer et al. (2020), DOI [10.1093/gji/ggaa359](https://doi.org/10.1093/gji/ggaa359), applied a three-channel correlation method to quiet, co-located iGrav records to estimate instrument-specific self-noise. The text reports average levels near -180 dB relative to `1 (m s^-2)^2 Hz^-1` from `10^-3` to `10^-1 Hz` for iGrav015 and iGrav032 at J9. This converts to PSD `10^-18 (m s^-2)^2 Hz^-1` and ASD `10^-9 m s^-2 Hz^-1/2`.

This is an extracted self-noise anchor, not total coastal station noise. The same paper identifies parasitic resonances and warns that noncoherent environmental noise can remain in the estimate. Paper 1 must eventually show both this best-case/self-noise category and empirical site-noise curves.

## AQG-A01 and FG5#228

Ménoret et al. (2018), DOI [10.1038/s41598-018-30608-1](https://doi.org/10.1038/s41598-018-30608-1), report short-term sensitivities of 750 `nm s^-2 Hz^-1/2` for AQG-A01 and 450 `nm s^-2 Hz^-1/2` for FG5#228. They identify a constant PSD region from `5e-4` to `1e-2 Hz`; the reviewed Paper 1 curves use exactly that interval. They also report a 36 s effective FG5 sampling interval and AQG response decrease above about 0.05 Hz. AQG long-term stability below 10 `nm s^-2` is a different statistic and is not converted into ASD.

The manifest's lower white-band edge at `10^-3 Hz` is explicitly a modelling choice. It must be varied or replaced by digitized PSDs before final atlas claims.

## Atom-interferometric gravity gradient

McGuirk et al. (2002), DOI [10.1103/PhysRevA.65.033608](https://doi.org/10.1103/PhysRevA.65.033608), report 4 `E Hz^-1/2` sensitivity and better than 1 E accuracy for a 10 m differential atom-interferometer baseline. The manifest converts 4 E to `4e-9 s^-2` but assigns only a placeholder display band; the full response must be extracted before quantitative process SNR.

## GOCE EGG

Willemenot, Touboul & Josselin report a GOCE target of 1–5 `mE Hz^-1/2` from 0.005 to 0.1 Hz. The manifest uses the conservative 5 mE end (`5e-12 s^-2 Hz^-1/2`). This is a spaceborne mission/design benchmark at roughly 250 km altitude, not a terrestrial sensor; it must remain in a separate panel/category.

## Rules for atlas use

1. Never compare gravity ASD directly with gradient ASD without modelling the correct observable.
2. Never interpret a long-term stability/accuracy number as white ASD.
3. Never treat isolated self-noise as real coastal station noise.
4. Never extrapolate beyond a curve's declared frequency range.
5. Treat flat segments formed from scalar sensitivity as assumptions and include them in model uncertainty.

## HUST National Precise Gravity Measurement Facility

The Hubei Department of Science and Technology/HUST acceptance announcement dated 2023-10-24 states that the facility passed national acceptance review on 2023-10-18. It reports capability for global milligal-level and reference microgal-level gravity-data acquisition/evaluation/application, and describes work in gravitational-constant measurement, space electrostatic accelerometers, and cold-atom absolute gravimeters as internationally leading.

These are facility-level capability statements, not frequency-dependent instrument ASD/PSD. The record is saved in `facility_capabilities.json` with `noise_curve_eligible=false`. Paper 1 may cite it as a domestic collaboration/infrastructure benchmark, but quantitative SNR requires a separate instrument specification or empirical noise record from the facility.
