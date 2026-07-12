# Gravitational-wave facility environmental Newtonian-noise evidence

Audit date: 2026-07-12

## Observable boundary

Newtonian-noise work for laser interferometers generally predicts test-mass acceleration/displacement or equivalent interferometer strain after detector geometry and mechanical response are applied. These are not directly interchangeable with a terrestrial gravimeter's vertical-acceleration ASD or a gravity gradiometer tensor ASD.

The project therefore stores model metadata separately in `newtonian_noise_models.json`. No entry is loaded by the `NoiseCurve` registry, and no ocean-process SNR is computed from it until the complete transfer chain is implemented and tested.

## Atmospheric turbulence model

Brundu et al. (2022), DOI [10.1103/PhysRevD.106.064040](https://doi.org/10.1103/PhysRevD.106.064040), model atmospheric Newtonian noise for third-generation detectors. Their work explicitly extends frozen homogeneous/isotropic turbulence treatments with finite correlation time and vertical inhomogeneity. It predicts spectral density versus frequency, detector depth, wind and turbulence parameters and compares with the Einstein Telescope xylophone design.

The paper reports order-of-magnitude modelling limits and depth/wind sensitivity. It is suitable as a translated environmental-channel model only after equations, normalization, detector geometry, parameter cases and figure values are independently reproduced. It is not evidence for a single universal “ocean sensor noise curve.”

## Cosmic Explorer local-gravity budget

The Cosmic Explorer design review, DOI [10.3390/galaxies10040090](https://doi.org/10.3390/galaxies10040090), treats local gravity fluctuations from seismic and atmospheric fields as a low-frequency limitation. It separates Rayleigh and body waves and states required mitigation levels of 20 and 10 dB for ambient acceleration ASD anchors of `1e-6` and `3e-7 m s^-2 Hz^-1/2`, respectively. The assumed ambient infrasound pressure ASD is `1e-3 Pa Hz^-1/2`; no infrasound mitigation is assumed in the cited sensitivity budget.

These quantities are environmental inputs to a detector response model, not the final equivalent strain curve and not a direct gravity-observation ASD. Long-term site studies, wave composition, ground properties and infrasound are explicitly required.

## Implementation gate

Before adding either model to the atlas:

1. transcribe equations and units from the full source;
2. reproduce at least one published curve/case;
3. test acceleration/displacement/strain conversions and arm-length response;
4. preserve atmospheric turbulence, infrasound, Rayleigh waves and body waves as separate components;
5. label every case by site/environment and mitigation assumption;
6. never present the detector's equivalent strain sensitivity as a gravimeter noise floor.

