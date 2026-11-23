# MetStat — Spec-driven contract for unified NWP models and fullscreen controls
Status: SPEC ONLY / NOT DEPLOYED
Source of truth: metstat-nwp/docs/METSTAT_MASTER_REQUIREMENTS_1405-08-30_v1.md
Method: GitHub Spec Kit SDD; UI audit guidance: nextlevelbuilder/ui-ux-pro-max-skill
Date: 2026-11-22

## Constitution / non-negotiable invariants
1. Never add a second model button group. Move/reuse the existing control nodes.
2. Keep desktop-style multi-column layout on mobile, with deliberate horizontal overflow if necessary; no single-column rewrite.
3. Do not replace production index.html or rewrite the 4.4 MB JS bundle without an exact diff and rollback.
4. All existing five geographical menus, map layer toggles, timestamps, rain-map and station database must survive.
5. Model identity is logical (`ecmwf`, `gfs`), resolution is per-frame provenance, not a separate visible model.
6. No deploy/merge without CI, DOM visual tests, manifest tests and live-host verification. No fake map fallback.

## Specification: observable acceptance
- AC01: Exactly one ECMWF and one GFS visible option in the model picker, regardless of normal/fullscreen.
- AC02: Existing buttons are physically moved to a horizontal fullscreen top dock; old vertical dock contains no duplicate controls.
- AC03: Exit fullscreen restores original placement, event listeners, keyboard focus and selected model without cloning.
- AC04: Switching model preserves selected region, parameter and valid time where supported; unavailable field gives explicit reason.
- AC05: Legacy ecmwf9 -> ecmwf and gfs25 -> gfs URLs/bookmarks remain readable; do not delete old data.
- AC06: A displayed map carries source model, actual source grid, cycle, valid time, lead, units and checksum; 9/28 or 13/28 labels come from manifest only.
- AC07: All five menus work before/after fullscreen and at desktop/phone viewport; model dock never overlaps menu bar.
- AC08: Rain-map, station search and Excel export still work against the intended database; failures must be explicit.
- AC09: Loading and memory usage must not regress materially relative to measured baseline.
- AC10: No claim of world coverage without actual global data and validated extent.

## Technical plan — required integration seam
- Inspect actual DOM, styles and JS for #ms95-modelDock, #fsMods, #nvBar and identify the ONE canonical button parent; selectors are hypotheses until verified.
- Audit normal/fullscreen event handlers and CSS cascade (r93/r96/r97/r98/r120/r121).
- Define `logicalModelId` and `sourceResolution` separately in the manifest schema.
- Backend emits one logical model per frame with explicit provenance. Frontend maps old IDs to canonical IDs before rendering.
- Use move/appendChild of existing nodes, NOT cloneNode and NOT an additional button component; preserve original parent/sibling for restore.
- Build a single source-of-truth registry for model display labels and availability. No independent hardcoded UI lists.
- Apply styles only to scoped existing selectors. Use a non-overlap layout test at 832x384, 1366x768 and 1920x1080.
- Verify five menus, layers, station search, rain-map, historical bookmarks and fullscreen round trip.

## Task dependencies
T01 Baseline: read active HTML/JS/CSS, record all button groups and five menus.
T02 Document model manifest schema and aliases with backend PR #25, PR #14 compatibility.
T03 Add DOM unit/integration tests for exactly one canonical model control group.
T04 Implement backend actual per-field source QC and same-cycle fallback; include source provenance.
T05 Implement frontend canonical model registry and legacy alias compatibility.
T06 Move original model buttons into fullscreen horizontal top dock, restore on exit.
T07 Playwright viewport + keyboard + model switch + five-menu + rain-map regression suite.
T08 Compare against Figma reference once access is granted; use UI UX Pro Max to review design tokens and interaction states.
T09 Measure bundle load time and memory, run CI and staged smoke test.
T10 Only after explicit approval, deploy with cPanel backup, SHA256, target paths, rollback; verify live URL.

## Gate and rollback
BLOCK merge if any AC fails or no screenshot/DOM evidence. BLOCK deploy if host source cannot be verified. Restore original assets, manifest and index atomically if any menu, map, or rain-map fails after release.
