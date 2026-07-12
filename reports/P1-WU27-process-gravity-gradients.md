# P1-WU27 process-level direct gravity gradients, part 1

Status: analytic/volume gradient propagation implemented for four process primitives; moving Gaussian surface gradients pending

## Disk gradient

For a uniform thin disk with signed surface density `sigma`, radius `R`, and axial separation magnitude `h`,

```text
Tzz = partial g_z / partial z_observation
    = 2 pi G sigma R^2 / (h^2 + R^2)^(3/2).
```

It is even across the disk plane for positive mass, changes sign with surface density, approaches the equal-mass point-source gradient in the far field, and tends toward zero for the infinite-sheet limit away from the discontinuous plane.

## Process propagation

- periodic tide and storm-surge signals scale the analytic unit-sea-level disk `Tzz`;
- compensated internal-wave lobes use deterministic volume-cell tensor summation and scale the unit-density `Tzz`;
- landslide solid/water point pairs scale the exact final relocation tensor by the transition fraction;
- translating eddy and tsunami signals retain `gradient=None` until their moving Gaussian surface-cell tensor is implemented.

## Predefined acceptance checks

- Disk `Tzz` agrees with a central finite difference of the independently implemented disk gravity.
- At `100 R`, disk `Tzz` agrees with the equal-mass point tensor within 1%.
- Side-of-plane, density sign, infinite-sheet limit and singular-plane validation are physical.
- Process gradient arrays match time length and reject non-finite/mismatched values.
- Existing registered gravity experiments retain identical SHA-256 outputs after the optional-gradient API extension.

## Result

All checks pass. The optional field prevents missing gradients from being silently treated as zero. Full Paper 1 gradient completion requires moving Gaussian surface `Tzz`, gradient-instrument band coverage/SNR, and physical process priors.

