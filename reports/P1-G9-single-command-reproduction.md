# Paper 1 G9 single-command reproduction

Status: **pass** (2026-07-13)

Command executed on the AutoDL server from commit `9afd30b`:

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

The command was run twice consecutively on AutoDL. Both runs produced:

- 11-page PDF during the build log (final file 994,673 bytes);
- PDF SHA-256
  `075c4c1cae8119156dc9a5e0316d3a34e444052647ab20ed6782370882847028`;
- build-report SHA-256
  `5d88ee6dda411ae48682472b724337b11aef4a30aff21788d01acee9a7354845`;
- identical registered figure hashes on the second run;
- passing literature and observable audits;
- no undefined citations or references in the final LaTeX log.

The machine-readable command records and hashes are in
`reports/paper1_release_build.json`. Bulk BSH inputs remain on AutoDL; the build
uses their frozen registered compact outputs and does not move raw data into
Git.
