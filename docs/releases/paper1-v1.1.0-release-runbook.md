# Paper 1 v1.1.0 release runbook

The existing `paper1-v1.0.0` tag is immutable. Do not create or move
`paper1-v1.1.0` until all steps below pass.

1. Push the reviewed pre-release commits to `origin/main` and verify remote
   read-back of the expected commit.
2. Create a Zenodo draft deposition and reserve its DOI without publishing it.
3. Record the DOI, approved CRediT, funding, competing-interest and AI-assistance
   statements, plus the all-author approval date, in `submission_metadata.json`.
4. Add the DOI to `.zenodo.json` and `CITATION.cff`; set submission metadata to
   `complete_verified` only after author approval.
5. Run `make paper1-jog-release`. This regenerates figures/tables, checks E011,
   validates citations, references, figure checksums and manuscript numbers,
   and builds the main and Supplementary PDFs.
6. Complete `final_pdf_review_checklist.md` against those PDFs.
7. Commit the DOI, declarations, build evidence and reviewed artifacts; push and
   verify remote read-back.
8. Create an annotated tag on that exact commit:

   ```bash
   git tag -a paper1-v1.1.0 -m "Journal submission candidate for Paper 1"
   git push origin paper1-v1.1.0
   ```

   Use a signed tag only when the signing identity and public verification path
   are already configured; do not invent or silently create a signing identity.
9. Create the GitHub Release from the tag, publish the Zenodo deposition, and
   verify the DOI landing page, file list, license, author order and checksums.
10. Re-download the archived files, verify their hashes against the build
    report, and only then assemble the journal upload package.

If the DOI cannot be reserved before the final build, use a release-candidate
commit without the final tag. Insert the DOI and rebuild before tagging; never
move the final tag to a later DOI-bearing commit.
