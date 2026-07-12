# P1-WU34 mature elastic-load provider decision

Status: LoadDef v1.2.2 selected for integration audit; not yet scientifically enabled

## Decision

LoadDef is the primary candidate because its peer-reviewed implementation
computes load Love numbers and displacement/gravity/tilt/strain load Green
functions for a self-gravitating spherically symmetric Earth, and reports
independent checks against Guo et al. Green functions and SPOTL ocean-tide
loading. The public repository identifies release v1.2.2 (2024-10-21) and a
GPL-3.0 license.

Sources:

- Martens, Rivera & Simons (2019), DOI `10.1029/2018EA000462`
- `https://github.com/hrmartens/LoadDef`
- `https://www.umt.edu/martens-lab/software.php`

## Critical mapping gate

The project interface currently preserves direct attraction, deformation
gravity, internal-mass gravity, and vertical displacement separately. LoadDef's
documented `gE` elastic-gravity Green function must not be arbitrarily split
into the project's two elastic gravity terms. Its equations, normalization,
reference frame (CE/CM), and source implementation must first be audited to
prevent component duplication or invented decomposition.

## Installation state

The release cannot be cloned from the current control plane because DNS access
to GitHub is unavailable. The manifest therefore records `selected-not-installed`
and requires the exact commit and artifact checksum after access is restored.
No LoadDef-derived scientific result is currently claimed.

## Acceptance sequence

1. Pin release commit and source checksum.
2. Freeze oceanless PREM variant, forcing convention, and reference frame.
3. Verify distance/unit normalization and near-load behavior.
4. Resolve `gE` component semantics against the paper and source.
5. Reproduce one published Green-function benchmark.
6. Only then adapt output into the project provider interface.
