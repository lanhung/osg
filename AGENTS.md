# Ocean Gravity Program agent rules

These instructions apply to the entire repository.

## Scientific scope

- Treat `claims.yml` as the authoritative novelty boundary. Do not introduce a title, abstract claim, figure caption, or README statement that conflicts with it.
- Do not describe a result as "first", "novel", or "unprecedented" without a separately documented literature audit approved by a human researcher.
- Paper 1 establishes the shared physics and instrument foundation. Do not add machine learning to Paper 1.
- For Paper 3, establish physical and multi-station statistical baselines before adding a GNN. A model must not be used to manufacture detectability where realistic-noise SNR is absent.

## Work-unit contract

Each implementation task should contain:

1. one bounded physical or data-processing function;
2. explicit inputs, outputs, units, and conventions;
3. an analytic solution, limiting case, or precise literature benchmark;
4. automated tests with tolerances chosen before observing production results;
5. a compact validation report or machine-readable metrics;
6. no unrelated module changes.

Code completion alone is not a scientific gate. Report which validation gate was passed and the evidence.

## Numerical and unit conventions

- Kernels use SI units unless an API explicitly states otherwise.
- Convert display units such as microgal only at I/O and plotting boundaries.
- State coordinate frames, sign conventions, Fourier normalization, one-sided versus two-sided PSD, and amplitude versus power spectral density in public APIs.
- Preserve direct attraction, deformation, potential response, atmospheric loading, hydrology, and ocean response as separate components until the final documented sum.
- Check atmosphere-ocean products for inverted-barometer or other coupled responses before summing them; never double count a load.

## Validation

- Place fast behavioral tests in `tests/unit/`, analytic and literature comparisons in `tests/physics/`, and reviewed frozen results in `tests/regression/`.
- Every scientific test documents source assumptions, units, expected result, and tolerance.
- Include zero, sign, symmetry, far-field or near-field, resolution-convergence, and conservation checks where applicable.
- A negative detectability result is valid. Do not remove an ocean process or earthquake scenario merely because it is undetectable.

## Data and reproducibility

- Never commit raw or bulk derived data, credentials, access tokens, station-restricted data, or private keys.
- Add a manifest before using a dataset. Record source, product/version, query, time range, spatial bounds, license/access terms, and checksum.
- A formal experiment records the full Git commit, immutable environment or image digest, data manifest, configuration, seed, UTC start time, machine, and outputs.
- Production figures and manuscript numbers must be reproducible through a registered workflow. Refuse to run an unregistered experiment silently.

## Change hygiene

- Preserve user changes and avoid broad formatting or dependency churn.
- Do not add GPU or distributed execution to CPU/I/O-bound work merely because GPUs are available.
- Do not commit, push, download restricted datasets, or start expensive AutoDL jobs unless the user explicitly requests that external action.

