# P1-WU74 persistent bundle recovery test

The Paper 1 v1.1 working history through commit
`85bbf1c9ce2577ac998cf7641e3c4180f4c468e0` is preserved outside `/tmp` at:

`/root/os/backups/osg-paper1-v1.1-full-85bbf1c.bundle`

- SHA-256: `74bf55fa04cab6a61433febc1ec7964049f5c9252d32364355152e331174a677`
- Size: approximately 5.3 MB
- Contents: complete `main` history and the immutable `paper1-v1.0.0` tag
- `git bundle verify`: pass; the bundle records a complete history
- Recovery clone: pass with `git clone -b main`
- Recovered HEAD: `85bbf1c9ce2577ac998cf7641e3c4180f4c468e0`
- Source HEAD at verification: `85bbf1c9ce2577ac998cf7641e3c4180f4c468e0`
- Recovered tag inventory includes `paper1-v1.0.0`

The earlier 521 KB `origin/main..main` bundle is only an incremental transfer
bundle and requires commit `844143d194805ea95046f81cac00f5e49c16bb12`; it is
not treated as a standalone backup. Restore the persistent bundle with:

```bash
git clone -b main /root/os/backups/osg-paper1-v1.1-full-85bbf1c.bundle osg-restored
```

This backup must be regenerated after the DOI/declaration commit and before the
final v1.1.0 tag.
