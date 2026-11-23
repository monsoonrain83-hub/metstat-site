# MetStat UI — phase 1 review (not deployed)

This is a non-destructive, CSS-only candidate extracted from the user's r193 reconstruction. It has **not** been reconciled with the current binary `site_src.zip` in main and must **not** be installed on production as-is.

- Candidate: `ui_phase1.css`; append only after reconciling with current `site/src/css/app.css`.
- Scope: focus-visible, overflow controls, narrow-screen model selector, reduced motion.
- Unchanged: JS, PHP, API, NWP map logic, data, routing, model computations.
- Existing desktop-phone (`dskPhone`) behavior is intentionally not overridden.
- Local build succeeded from r193 reconstruction; no real-device browser or production regression test completed.
- Production deployment workflow automatically builds and FTPS-uploads on main changes to `site_src.zip`, `site_src.part*`, `site_patch*.zip`, or `nwp_upload.php`. This review branch deliberately does not change those paths.

## Next gate
Obtain the latest deployed source, compare selectors, run desktop / mobile / mobile desktop-site tests, and only then prepare a reviewed deployment artifact.
