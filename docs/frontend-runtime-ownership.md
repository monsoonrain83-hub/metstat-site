# Runtime ownership audit (approved V85 core)

Baseline: assets/ms_r5_perf_core_cf0e22054ebb398d.js, SHA-256 cf0e22054ebb398d39d5ff12501a2f1cb2b7229e907c3bdc02121966b2a1ac05. Static source audit only, not a CPU attribution of all listed code.

## Next target: R5 sidebar rendering
- `nvFrSync` (around line 16013) calls `nvrSync(false)`.
- The image resolve path (around line 16059) calls `nvrSync(true)` after drawing.
- `nvrSync` (around line 25242) includes `NV.s.fr` in its render signature. Consequently, a frame change invalidates the entire sidebar, including mirrors, period buttons, radio model rows and parameter accordion. The forced image-resolve call also bypasses the signature.
- `nvrParamRender` replaces every child of `msR5ParamPicker`. The old `nvWx` controls are still present but not the current visible R5 interface.
- Separate structural state (available models/runs/categories/parameters, locale, manifest generation, expanded groups) from selected frame/time-label state. Update only changed subtrees and preserve focused buttons. Use actual current R5 controls in browser tests. Do not simply delete the frame component of the signature: first confirm all consumers, run/locale/status changes and control validity.

## Timers and observers
The core contains 27 setInterval call sites and 13 MutationObserver construction sites (static counts, not active instances).
- Intentional animation: forecast and satellite playback, live map, synoptic playback; must stop when page is inactive and preserve user-selected rate.
- Data refresh: forecast every five minutes, satellite refresh, climate products and mailbox; preserve freshness, single-flight and visibility checks.
- Bounded waits: combined-map completion and immersive-view readiness; preserve timeout and cancellation.
- UI polling: clear-button checks (600 ms), visual tab sync (1500 ms), two navigation sync loops (1500/1200 ms), layout fix (500 ms and 2000 ms), other sync (800 ms). These are review candidates, not safe deletions.
- Whole-body mutation watchers and per-page visibility observers may overlap. Map each owner before reducing them; preserve localization, account-state and accessibility behavior.

## Test requirements for the next extraction
Compare exact options, status classes, selected controls and map/export results across current/previous runs, languages, frame steps, model/parameter changes, zoom/region, page switching and fullscreen. Assert stable DOM identity for unchanged controls and no increase in long tasks. Measure before/after on identical data. No parallel DOM compatibility layer or new permanent polling interval.
