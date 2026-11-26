# Frontend source and release migration

## Decision
Do not install new compatibility overlays to fix existing overlays. Refactor one behavior at a time, replacing its implementation under its existing interface. Keep the user-approved R5 desktop layout on all devices and the meteorological calculations/output contract unchanged unless separately authorized.

## Source ownership
- `web/forecast/frame-index.mjs` owns the shared Middle East / Europe lookup. The builder embeds it once into the classic bundle and replaces the legacy ME/EU implementations. The existing `nvMeItems` and `nvEuItems` names are thin bridges, not alternate engines.
- A new manifest or replacement array invalidates the cached index. Any future in-place edit of row keys must call `invalidate()`. The loader's current replacement behavior is preserved. Unit tests cover both run selections, filters, exact order, row identity, independent result arrays and invalidation.
- The R5 parameter accordion (`msR5ParamPicker`) is the visible UI. The retired hidden `nvWx` panel is not an acceptable target for an interaction smoke test. Its remaining dependencies must be mapped before removal; do not delete it yet.
- The remaining core is still a legacy generated bundle. This is a first extraction, not a completed frontend rewrite. The temporary SHA-pinned integration builder is required until the entire approved source baseline is versioned. CI must not deploy it automatically.

## Release contract
1. Establish exact approved production baseline (HTML/core SHA-256). If it differs, stop.
2. Generate one candidate from source; no manual edits after browser testing.
3. Test unit contracts and identical frame/menu outputs on one captured manifest. Test physical model, parameter and time controls, map rendering, PNG, desktop and touch.
4. For core-only changes, accept exactly `index.html` and the one content-addressed core. Reject extra paths, symlinks, duplicate names, invalid hashes, unexpected HTML changes or retired deployment files. Record complete hashes in a separate provenance artifact.
5. Keep the previous approved release outside public_html; deploy ZIP through cPanel only after the tests pass. Confirm live hashes and browser behavior after deployment. Rollback means the exact immediately preceding approved release, not an old full archive.
6. Never mix PHP, database, NWP scientific changes or admin authentication with a narrow core release. UI structural changes require an explicitly scoped release contract and regression tests.

## Next extraction boundaries
Catalog and data selection; map interaction/rendering; R5 control ownership; optional assets; export; page lifecycle and timers. Establish one owner for each event and timer before removing compatibility code. Measure CPU and long tasks; no invented performance gains. Preserve legacy routes until tested. Persist immutable source baseline and reproducible release artifacts before deleting legacy code.
