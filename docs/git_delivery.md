# Git and GitHub delivery rules

- Primary branch: `main`.
- Remote delivery target: `origin` (`git@github.com:lanhung/osg.git`).
- Each commit represents one reviewed work unit or one coherent project-control update.
- Push only after local tests, compilation, whitespace checks, and secret scanning pass.
- Never force-push shared history.
- Never commit the deploy private key at `/root/os/.deploy-keys/lanhung_osg`.
- Large or restricted data are represented by manifests and checksums, not Git blobs.
- Compact derived metrics and small reviewed fixtures may be committed when their provenance and license permit redistribution.
- Manuscript-facing figures must identify the experiment metadata that generated them.

The machine-local deploy key has write access and is configured through this repository's `core.sshCommand`. Git author identity is separate from SSH authentication.

