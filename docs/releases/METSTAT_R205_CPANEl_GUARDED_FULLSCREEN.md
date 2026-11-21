# MetStat r205 — guarded fullscreen chip release (21 November 2026)

**Scope:** Move the **existing** colored #fsMods model chips into the original fullscreen top row; do not clone controls, change NWP/SEAS5 data, change model selectors, or overwrite the canonical 6.3 MB index.html.

## Verified input / source of truth
User-provided index(20261121-142945).html (SHA256):
`2ca1e49e1542bfd1664633b656ce504dfbe93f1ec184c9baf8e90ea4c84bf5fc`.
The index already references `assets/metstat_original_model_chips_horizontal.css?v=20261121` and the same JS with `?v=20261121`, each once. Its nvfBuild() creates #nvFs lazily and moves #fsMods into .fsColR .fsModDd; the r205 script relocates that SAME node to .fsRow.fsA.

## Files on cPanel
Upload only:
- `assets/metstat_original_model_chips_horizontal.css`
- `assets/metstat_original_model_chips_horizontal.js`

Upload CSS first, then JS. Backup both originals and index.html outside webroot first.

A release asset ZIP with SHA256 manifest and offline CLI-only guarded index version bump is delivered separately to the site operator. For a 100%-matched live index, update ONLY the two asset query versions to `?v=205.0` (strict SHA256 guard; hashed index after exactly those two substitutions: `4484371420ab2f00f278ab0807d1a299be6a82767cd0f6f3f3aa086902c9dc6c`). Do **not** upload an arbitrary overwritten index.html, leave a public PHP installer online, or publish without backup.

## QA result (LOCAL ONLY — not live host)
- Chromium loaded the **actual uploaded HTML**, executed its real nvfBuild(), and validated the relocated original node at widths 320, 360, 384, 540, 832, 1250 and 1920px.
- At every size: exactly one #fsMods, five buttons injected for test, model row horizontal/scrollable, old dropdown hidden AFTER successful relocation, Save button not overlapped.
- On unexpected DOM, fail closed: no CSS marker and old dropdown stays visible.
- CLI preflight test: check/apply/idempotent apply/rollback/idempotent rollback, modified-index guard and wrong-asset guard PASS.
- `node --check` and `php -l` PASS.
- Site GitHub-hosted Actions continue to fail **before any steps run** (empty steps; 404 BlobNotFound log); private-repo billing/quota or runner provisioning suspected, **not confirmed**.

## Rollback
First revert the two index query versions / run CLI rollback while the r205 assets remain installed, THEN restore backed-up JS/CSS. If live index differs from the SHA baseline, **stop** and request the currently deployed index for review.

**Not yet verified:** real host cache, mobile tapping of all controls with actual NWP data, live regression of region/zoom/capital and model run selectors. This release is a production-scoped, guarded manual deployment artifact, not a claim that host verification is complete.
