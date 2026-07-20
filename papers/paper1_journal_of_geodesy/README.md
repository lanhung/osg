# Journal of Geodesy revision package

This directory is the versioned `paper1-v1.1.0` journal-revision source. It is
deliberately separate from the immutable `paper1-v1.0.0` technical-preprint tag.

`main.tex` selects the journal title and reuses the maintained Paper 1 body so
that equations, citations and figure references cannot diverge between an
untracked upload and Git. `supplementary.tex` contains the process registry,
record composition, frequency statistics, instrument evidence and both
supplementary figures. Four tables are generated directly from frozen configs
and metrics by `scripts/export_paper1_journal_tables.py`.

The package is not release-ready while `submission_metadata.json` is incomplete
or P1-E011 lacks finalized registered metrics. After those gates close, run:

```bash
make paper1-jog-release
```

The command refuses unresolved citations/references, internal draft markers,
missing SI assets, missing author/affiliation metadata, a missing archival DOI,
or a non-public release tag.
