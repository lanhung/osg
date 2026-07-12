# P1-WU36 observable-separated instrument ASD figures

Status: deterministic SVG figures generated and tested

## Outputs

- `reports/figures/instrument_asd_vertical_gravity.svg`  
  SHA-256 `a749d7705b80fe087f9a2668ea7d3fe15eb0e895ad4aec52da115d301aebeb96`
- `reports/figures/instrument_asd_gravity_gradient.svg`  
  SHA-256 `489e0a927fcbf6b5ca722743ceef3ea0b8ac2c6ee04867f721776bdf58230bbd`

The renderer uses logarithmic frequency and ASD axes and draws vertical gravity
and gravity gradient in different files. Tests prohibit gravimeters appearing in
the gradient panel and prohibit gradient instruments appearing in the gravity
panel.

## Interpretation limit

These figures visualize the five versioned literature/model anchors exactly as
encoded; they are not final site noise curves. Flat two-node lines expose the
current simplifying assumptions and must not be read as measured whiteness
beyond the documented bands. The GOCE curve remains a spaceborne design anchor,
not a ground-instrument claim.

## Reproduce

```bash
python3 scripts/render_instrument_noise_curves.py \
  --manifest data/manifests/instrument_noise_curves.json \
  --output-directory reports/figures
```
