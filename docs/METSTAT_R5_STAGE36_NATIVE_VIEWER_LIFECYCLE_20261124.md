# R5 Stage36 — native NWP viewer lifecycle, no duplicate listeners, no polling (2026-11-24)

**State:** exact cPanel-source *candidate*, delivered as verified ZIPs to the administrator in ChatGPT. No deployment, no NWP/API/host-PHP integration test, no new meteorological product.

## Motivation / proven regression
The Stage35 actual inline `nvInit()` invoked `nvBindStage(stage)` on every initialization. The same `nvStage` DOM element accumulated 7 pointer/wheel/click listeners per call: **7 after first, 14 after second**. At the same time a permanent `setInterval(nvfBtnLab,600)` ran on every page, and `nvLeave()` did not release its current `ResizeObserver`.

## Exact bounded modifications to Stage35 host HTML
- `nvBindStage(st)` adds an element-owned `st.__msNvPointerBound` idempotency guard; a brand-new DOM stage still gets its own listeners.
- `nvLeave()` disconnects and nulls `NV.resizeObserver`; `nvInit()` already creates the new observer when re-entering.
- `nvInit()`, `nvfEnter()`, `nvfExit()` synchronize the same original fullscreen button label. Remove the `600ms` polling timer and unnecessary `50ms` label timeout; preserves original button, original `nvfToggle`, Escape/fullscreenchange and real fullscreen DOM flow.
- Only **one inline script block** differs. No CSS, font, GIS data, weather model, forecast transform, API, external asset, new control, DOM ID or `!important` modification.

## Evidence
- Stage35 browser test with two calls to `nvInit` on same DOM: **7→14** listeners; 2 ResizeObservers created, 1 disconnected on `nvLeave`.
- Stage36 equivalent on 1440×900, 960×720, 844×390, 390×844: **7→7** listeners; 2 created, 2 disconnected on `nvLeave`; same 7 main menu groups, five geo selects, no pageerrors, 19 inline script tag bodies parse with Node.
- Stage36 1440 desktop and 390 portrait native functions: 2× `nvfEnter` + `nvfExit` cycles on actual original map: one `fsMods` node, map returns to original parent, the pre-existing animation timer remains the same while switching mode and stops when leaving; no pageerrors. Mock `ON.man` fixture only — **not a real forecast image/GIF test**.
- SHA-256 from exact source `Stage35 index.html`: `e2d95e51561b64fbaa449891c3957c337880353b027fd4581e5013810e8b0f9b`.
- **Stage36 target index.html SHA-256:** `f594a4aabdf8f77fe4dd17c8bd0b73fd39102830830a440f5c151445cdcd3893`.
- A direct four-file overlay exists for original source SHA `a6d3c06bb3197671e2a7e1f3e2043b924a23ee35c76ca4f35ef9d1e1c66a90d8`. A one-file overlay exists for matching Stage32, Stage33, Stage34, Stage35 baselines. Rollback ZIPs are **independent for every baseline**; do not mix them. Uploaded archive filenames, hashes and install path are in Persian install guide delivered separately.
- `tools/r5_stage36_host_gate.py` checks exact baseline SHA and ZIP shape, no unsafe path/PHP, target SHA and native behavior invariants; `tests/test_r5_stage36_host_gate.py` covers negative cases. Run on PR (actual full host file not in git).

## Hard deploy gate
Reject deployment if active cPanel SHA does not match specified source, if the R201/stage24 assets differ from expected matching source versions, or if hosting automation has already installed another index. Back up all overwritten files **outside webroot**; stage before production. Verify exact direct route 200, actual model/valid-time/extent/provenance, animation/GIF/PNG, UI FA/EN, right-sidebar, fullscreen, GIS boundaries, isohyet/verification/toolbox, PHP/auth, Android physical gestures and rollback. **No claim of completion** until live acceptance is completed.

Full R5 migration and priority scientifically correct global NWP resolution fallback/DEM/seasonal anomalies remain separate roadmap work.
