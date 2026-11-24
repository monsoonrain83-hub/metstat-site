# MetStat R5 Stage37 — transient forecast image retry / empty-frame busy recovery

**Date:** 2026-11-24. **State:** SHA-pinned **host candidate** for administrator review and isolated staging, not deployed.

## Correct source and tested failure

The source is the cPanel `index.html` reconstructed exactly from the user-supplied `index(20261124-041820).html` + `assets.zip` and Stage32–36 overlays. We verified the full Stage36 source SHA-256 `f594a4aabdf8f77fe4dd17c8bd0b73fd39102830830a440f5c151445cdcd3893` before editing.

1. Existing `nvImg(url)` stored a resolved `null` promise in the shared 60-entry `NV.cache` after `Image.onerror`. The same image URL never retried until unrelated cache eviction/page reload. This could make a newly published forecast frame appear permanently unavailable after a brief 404/CDN/network glitch. Reproduced with a mocked Image in Chromium: **first request failed, second request did not occur (1 total)**.
2. In `nvResolve()` the `!cur` branch did not set `NV.busy=false` or hide `#nvBusy`. If it invalidated a prior in-flight tile request via `++NV.tok`, the stale completion could not unlock the UI; playback skipped frames and the spinner remained. Reproduced with the actual original viewer DOM and control state.

## Exactly two code modifications, same original owner

- For `nvImg`, attach a `.then(img => ...)` result handler and delete only a **failed** entry whose promise still equals `NV.cache.get(url)`. Successful promises stay shared/cached, in-flight identical URLs coalesce and the 60-entry bound remains untouched. No retry polling or new timer introduced.
- For `nvResolve` `!cur` branch, clear busy state and hide the existing spinner, with the existing token guard continuing to prevent stale responses.
- One inline JS section changed (script index 11). **All CSS byte-for-byte identical to Stage36; 1,138 existing `!important` unchanged**, no extra DOM controls, no model/GIS/DEM/scientific formula modification.

## Reproducible acceptance

**Chromium 4 viewport × 2 candidate versions = 8 before/after browser fixtures:**
- 1440×900, 960×720, 844×390, 390×844.
- Stage36: first simulated image load fails; failure remains cached; second load still fails without a second network request; empty-frame case `NV.busy=true`, spinner visible.
- Stage37: failed image evicted; second request succeeds (2 network requests total); successful image cached; concurrent shared URL deduplicated; empty-frame case `NV.busy=false`, spinner hidden.
- No browser page errors in any case.
- Repeated `nvInit()` at all 4 Stage37 viewports: 7→7 pointer listeners, 2 observers created/2 disconnected after leave; original fullscreen button labels and 5 selectors/7 nav groups intact.
- 19 inline JS bodies syntax-checked (Node); only one original script changed.
- The scripts/test fixtures, exact unified JS diff, screenshots, report and manifests are in a **QA-only ZIP** delivered in chat, not deployed.

## Deployment gate

- Target index SHA-256 **`a6ee0843b29c300ec083ef0d7c636eb759ee4dd3eb9ea90d38079d5240243aa1`**.
- Direct original-host 4-file installer only if active index SHA `a6d3c06bb3197671e2a7e1f3e2043b924a23ee35c76ca4f35ef9d1e1c66a90d8` AND original R201 CSS/JS + restore module match exact initial asset hashes.
- Single-file installer only when active index matches **exactly one** of Stage32, 33, 34, 35, 36 hashes and existing Stage32 assets match their SHA. Separate rollback ZIPs for all six baselines.
- Unknown source => **stop**; do not overwrite automation or other developer's updates.
- `tools/r5_stage37_patch.py` is the idempotency- and checksum-guarded candidate build script, **does not deploy**. `tools/r5_stage37_host_gate.py` + tests reject unsafe ZIPs, unknown hashes, missing retry state and stuck spinner. GitHub Actions was green as of run 45343795229.
- **Not tested:** active cPanel after admin upload, actual live tile/CDN, HTTP 404/500, auth/PHP, full-scale model provenance/resolution, PNG/GIF production, physical mobile gestures, or complete R5 visual acceptance. Web retrieval of the exact public model URL in this turn was unsuccessful.

## Next prioritization, as per unified roadmap

P0/P1 live route/API verification and genuine PNG/GIF output on an isolated staging site remain required. P4/P5 must implement real ECMWF/GFS per-variable, per-run, per-lead resolution fallback, real source/grid/extent/QC metadata, unique manifest frames and ERA5 anomaly provenance: this Stage37 client retry does **not** substitute for any of them.
