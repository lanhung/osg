# Paper 1 G9 single-command reproduction

Status: **pass** (2026-07-13)

Final release command executed on the AutoDL server from commit `dfbe314`.
The earlier G9 workflow was also run twice consecutively with identical hashes;
the release run revalidated the expanded P1-E010 package:

```bash
/root/autodl-tmp/ocean-gravity-run/venv/bin/python \
  scripts/build_paper1_release.py \
  --python /root/autodl-tmp/ocean-gravity-run/venv/bin/python
```

The equivalent repository target is `make paper1-release`.

The workflow validates the experiment registry, audits the literature and
observable ledgers, regenerates all five main figures and two supplementary
figures from frozen registered metrics, runs BibTeX and three LaTeX passes, and
fails on undefined citations or references.

The final release run produced:

- 12-page PDF during the build log (final file 1,001,252 bytes);
- PDF SHA-256
  `a09f0c7207127ca0a2c480d7347a72851687dbef9fa4264b7592fbac9947103a`;
- build-report SHA-256
  `f2b17175911f8718edd928313dd346a0b25a9d0ab45bc18aca37a9bf30f0b8fb`;
- 453 passing tests on AutoDL;
- passing literature and observable audits;
- no undefined citations, references, warnings, overfull or underfull boxes in
  the final LaTeX log.

The machine-readable command records and hashes are in
`reports/paper1_release_build.json`. Bulk BSH inputs remain on AutoDL; the build
uses their frozen registered compact outputs and does not move raw data into
Git.
