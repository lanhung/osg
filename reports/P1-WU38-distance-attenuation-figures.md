# P1-WU38 distance-attenuation figure pipeline

Status: deterministic engineering panels generated and tested

## Outputs

- Direct gravity: `reports/figures/distance_attenuation_gravity.svg`  
  SHA-256 `4c7280ac5b383ef9c0a65aa48d240813a71b306e8dd51286f7438af0e8ad36ec`
- Gravity gradient: `reports/figures/distance_attenuation_Tzz.svg`  
  SHA-256 `3fc4caf2162e224f62c0292e7447b79bf6150fa1a55a1bb85ab025aca975dbc1`

Both panels use logarithmic axes, include all six processes and all seven frozen
standoffs, and read only the registered `P1-E004` metrics. Tests require every
process label and the correct observable units.

## Interpretation

These are engineering foundation panels. Their purpose is to verify the future
atlas figure contract and expose process-dependent compensation/attenuation.
They must be regenerated after cited scenario envelopes, elastic response, and
realistic sensor geometry are integrated.

## Reproduce

```bash
python3 scripts/render_distance_attenuation.py \
  --metrics experiments/paper1/P1-E004-distance-attenuation-foundation/metrics.json \
  --output-directory reports/figures
```
