# MetStat R5 Stage41 — accessible native settings and stable seasonal controls

**Date:** 2026-11-24 | **Status:** reversible offline candidate; no live cPanel installation, no merge. R5 remains sole UI source of truth.

## Reproducible defects in Stage40

A real offline Chromium fixture that executes original native `caLayoutSplit()` and `sfRender()`, with actual existing card/container classes and harmless representative controls, established:

1. **Climate atlas**: `#caApp .panel>h2` only had `onclick`. The heading was not keyboard focusable and Enter/Space did nothing. Mouse collapse toggled CSS `.pcol` but had no ARIA state. All Atlas settings remain in two native groups (`#caAside`, `#caAside2`) in one **right column**; output remains the original left `<main>`.
2. **Monthly/seasonal forecast**: `sfRender()` set `st=!keepOpen`, collapsing essential right-side `.sfSet` controls on first load, and `.card>h3` also used pointer-only `onclick`. State keys were based on `h.textContent.trim().slice(0,30)` and lost their identity when Persian changed to English.
3. Neither page provided a reliable visible focus ring on these disclosure headings.

Stage40 passed only **5 of 11** targeted acceptance assertions per viewport in this interaction-specific fixture; a previous static geometry smoke did not test these interactions and should not be represented as full UX acceptance.

## Strict Stage41 changes

- Original Atlas `caLayoutSplit()` assigns `tabIndex=0`, button role, `aria-expanded`, a single reused toggle and keyboard Enter/Space behavior **to each existing heading**. Already-bound heading nodes are skipped via the existing `dataset.tg` guard. Mouse behavior remains intact; no new buttons, duplicate listeners, timers or observers.
- Original `sfRender()` uses stable semantic card keys: `settings / indices / method / forecast / scenario` and a safe index fallback. The right-side **settings** and left-side **forecast viewer** begin expanded; supplementary science methodology and custom scenarios may be collapsed and manually expanded. User state survives FA/EN and same-page redraw.
- Only the existing `ms9-desktop-r5-system` style owner gains `:focus-visible` outlines for Atlas and seasonal headings. **No `!important` added** (1,138 remain).
- **Only inline JS section 11 and CSS style section 5 changed** from Stage40. All other HTML, original model controls, DOM IDs, geographic selectors, GIS, climate/rainfall scientific formulas, PHP, assets and existing panels are unchanged.
- Original R5 reference file SHA256 `2792e674660f07135acb91f6cbf92f8740f4c9ff8c073e94767927b1c8dbadf9` remains canonical; **desktop-style two columns on all devices** (390px portrait uses a scrollable 960px canvas), no one-column mobile substitution.

## Exact checksum release gate

Stage40 source index SHA256 `3b80f0e8db2334e1e0a0febe3acd17f84ba89dcac09b2f1632353f61d8859958` → **Stage41 target index SHA256 `7ff4bbfeb3b658ca8d36c6da3efa6bb83d7ffbca1cebcf8403ec2dff80f1c295`**.

The ChatGPT-delivered ZIP artifacts support exactly these active index baselines: administrator original, Stage37, Stage39 (regressed Atlas), Stage40. All other hashes, including hourly modified hosts, must be rejected. The original-host installation ZIP contains the index and the three pinned R201/Restore assets; incremental versions contain only `index.html`; each original baseline has a dedicated rollback ZIP. ZIP CRC, exact paths, source/target SHA are verified. **Do not deploy without separate exact asset SHA checks, live-host snapshot/rollback and admin approval.**

Permanent source and CI artifacts:
- `tools/r5_stage41_native_panel_patch.py` reproducible Stage40→Stage41 patch, refuses unknown source SHA, duplicate owner anchors and changed JS/CSS ownership.
- `tools/r5_stage41_host_gate.py` verifies host ZIP and all Stage37–41 invariants; `tests/test_r5_stage41_host_gate.py` covers negative cases including regression to translated labels or hidden settings.
- `tests/test_r5_stage41_native_panel_patch.py` tests one-time application and exact ownership. GitHub Actions gates run with the existing R5 workflow; no host actions.
- All browser fixture scripts and JSON evidence supplied in the QA-only ZIP, **not for public webroot**.

## Offline acceptance evidence

- Actual original Stage40 vs Stage41 code tested at **1440×900 / 960×720 / 844×390 / 390×844**: Stage41 **11/11** interaction assertions at all four viewports; Stage40 **5/11**.
- **48/48 Enter/Space operations** successful on six representative original Atlas/seasonal headings (six headings × two keys × four viewports), including ARIA state updates and focus.
- Browser checks cover idempotent Atlas callback rebind, mouse parity, two-column atlas with dynamically inserted `#caAside2`, actual `sfRender()`, settings initially visible, state retained after re-render with translated Persian headings, expected 390px intentional horizontal canvas and no browser JS errors.
- 12 route modules × four viewports = **48** smoke tests; **44/44 non-Atlas route geometries** (grid, original control positions/visibility, document width) unchanged from Stage40.
- Node.js syntax-check: all nonempty scripts in 19 tags pass, only inline JS #11 and CSS #5 modified, existing 1,138 `!important` unchanged.

## Not yet accepted

This is **offline UI source testing**. It does NOT prove real Atlas station DB load, SEAS5/ERA5 product freshness/calibration, download PNG/GIF, browser navigation of every real route, authenticated API, any direct HTTP 404 result, cPanel security, physical Android pinch/scroll, or full Figma design parity. Connected Figma still returned no Editor access; the GitHub UI UX Pro Max rules are supplementary QA, **not a replacement for R5 or admin-approved workflow**.

Next release gate: inspect hashes of the *currently live* index, assets, .htaccess, render on authorized staging with genuine data/API, validate existing isohyet/verification/toolbox/stations and all online model map controls, then backup and obtain administrator approval. Do not call the site deployed or scientifically verified on the basis of a green offline CI.
