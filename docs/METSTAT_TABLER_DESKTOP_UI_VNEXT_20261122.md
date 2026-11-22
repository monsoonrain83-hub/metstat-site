# MetStat UI vNext — Tabler-first desktop shell and safe integration contract
Date: 2026-11-22 (1405-09-01)
Status: **design + isolated code review; not installed on live cPanel**

## Source and precedence
- Verified user-provided source archives: `tabler-dev.zip` (Tabler Core v1.7.5, MIT); `ui-main.zip` (shadcn/ui, MIT); `magicui-main.zip` (Magic UI, MIT).
- Tabler is the **primary design language** (navigation/card/form density/status pills/RTL). shadcn/ui contributes accessible tokens/disclosure/switch patterns. Magic UI contributes subtle animated expansion and loading status, disabled under `prefers-reduced-motion`. **Do not inject React/Framer/Tailwind into the existing monolithic browser runtime without architecture review.** No third-party `@latest` CDN in production. Vendor/build pinned, reviewed same-origin assets and retain licenses.
- This explicit **new** administrator requirement **supersedes** the older horizontal fullscreen colored model chips in r205 and the master requirements section 8.2: the **original** colored model chips must be a **vertical rail at the right INSIDE the map canvas**, in normal and fullscreen modes. Never show the old horizontal row AND the vertical chips together. Preserve original IDs/listeners, never clone the buttons.
- The persistent app uses a desktop-sized workspace on desktop, landscape phone, and portrait phone; **never responsive one-column stacking**. At narrow widths it must scroll horizontally with legible CSS pixel font sizes, not scale 1200 pixels into 390. All control groups remain bounded within their owning map/panel; avoid layout jumps.

## Stable design tokens
`surface:#fff; background:#f3f6fa; text:#152437; muted:#677990; border:#e4eaf1; accent:#3766e8; radius:9/14px; primary touch targets:40px minimum; body:14px (Persian system fallback); active status:#18a879; unavailable:#e45a68; partial:#448bda; updating:#f7b548`.
Status colors and blinking **must come from verified model/product availability** and the real UI state; do not present illustrative status as live.

## Unified shell structure
1. **ONE header row**: product mark, core navigations, language/account/status on opposite ends. Fixed layout height; no double row on phones.
2. Five dependent selectors **in one row above the map**: continent → region → country → province/state → county, with geo extent changes only when validated boundary and genuine map data are available. No fake zoom or silently incorrect bounds.
3. Forecast group contains product family (daily/weekly/monthly/seasonal/ensemble), **one ECMWF and one GFS option** (not separate resolutions), primary/secondary parameter, run and available lead/valid hour. Frame source/resolution must be shown from real per-field manifest.
4. Layer/display group contains counties, small towns, villages, roads, lakes, rivers, place labels, line thickness, label sizes and wind animation/speed. Gear/eye/layers icons have hover/focus and touch-tap text expansion and accessible `aria-expanded`/labels. Single disclosure panel closes on outside click/Escape.
5. Map **left rail** top-to-bottom: zoom-in, zoom-out, full extent, **refresh**. Map **right rail**: the original model status buttons in a vertical column, statuses green/red/blue/blinking for ready/missing/partial/updating. Footer colorbar has matching readable labels directly under the bar. No duplicate controls or invalid map scroll offsets.
6. The visual shell and accessibility affordances must be consistent across real forecast, station map, verification, climate, isohyet, synoptic, toolbox, and flood pages; do not change meteorological formulas, DEM, station resolver, or authentication.

## Canonical routes (all independently reloadable after authenticated release)
- `/monitoring-forecast/weather-models`
- `/monitoring-forecast/weather-models/daily`
- `/monitoring-forecast/weather-models/weekly`
- `/monitoring-forecast/weather-models/monthly`
- `/monitoring-forecast/weather-models/seasonal`
- `/monitoring-forecast/weather-models/ensemble`
- `/meteorological-tools`, `/synoptic-analysis`, `/climate-analytics`, `/rainfall-isohyet`, `/forecast-verification`, `/flash-flood`.

**NO blanket `.htaccess` rewrite.** Old `/monitoring-forecast/weather-models/online-maps` and other verified public bookmarks remain compatible aliases until: fresh live DocumentRoot/source hashes, production auth and front-controller identification, 200 on direct canonical load/reload, browser back/forward, logout, asset and PHP/API route tests, cPanel rollback. Only then add explicit targeted 301 redirects and retire obsolete routes. Preserve all private/auth/online endpoints.

## Safe development order and acceptance
- Read latest live `index.html`, `.htaccess`, `auth.php` if applicable, original `#nvFs`, `#fsMods`, map renderer, r205 styles and existing full path resolver. **The GitHub `site_src.zip` archive is stale and is not an acceptable production baseline.**
- Use a canary-only **opt-in** adapter for moving the *existing* model node to a **verified map canvas**; if missing or duplicated, do nothing (see `ui_patches/metstat_tabler_vnext_fullscreen_adapter.js`). It does not install a new map or buttons. Real control/boundary selectors must be determined from the live source, not invented.
- Unit + visual browser QA at 1920×1080, 1440×900, 1280×720, 844×390 landscape and 390×844 portrait. Check clipping, overlapping, jumps, touch expansion, focus/Escape, RTL/LTR, all new URLs and old aliases, authentication, actual region zoom and real model data.
- Run on staging, compare screenshots/DOM/performance before vs after, verify no new 404s; preserve backup+hashes+rollback. **Production deployment requires explicit release readiness checks; do not auto-merge this draft or blindly update live files.**

## Current deliverable
A separate interactive static prototype (HTML/CSS/JS + 12 local structural, HTTP route, security syntax smoke tests) is provided to the administrator as `MetStat_Tabler_UI_vNext_20261122_PREVIEW.zip` outside this repo. It is **not a deployable site update**. This repo branch deliberately contains a guarded migration building block and spec only, avoiding a mass `index.html` overwrite. The assistant's Chromium is managed by URLBlocklist and could not run visual E2E; that QA remains pending.


## vNext2 / 2026-11-22 — Sky White Scarlet overriding visual tokens

**This section supersedes the earlier "Stable design tokens" values for visual chrome only.** User supplied exact three colors: Sky Blue `#399FD4`, Paper White `#F8F9FD`, Scarlet Red `#DC1937`. White text embossed on the main blue header; all normal unselected buttons/menus white with scarlet ink, pressed/selected buttons scarlet with white ink. Exclude original status model rail `#fsMods` and `.ms-rail-chip` from site theme overrides. Preserve green/red/blue/flashing status colors from real model data.

Top-level-only horizontal header navigation and click-to-open cascading subpages, Escape/outside click dismissal. Categorized main/secondary parameter choices, `details/summary` plus/minus. Compact forecast lead range timeline moved directly under map, with previous/next/play/pause and configurable lead step; real model/run/field manifest must dictate available leads. Wide dropdown map colorbar with genuine palette strips in the list; when closed, the actual color strip and verified numeric ticks remain horizontally underneath. In preview the existing site `MT_PAL_LIB`, `MT_PALS`, `MT_PAL_EDGES`, WeatherBELL `WB_PAL` and snow palettes were extracted from administrator-owned `MetStat_P18_COMPLETE_LAYOUT_TEST.html`: **41 palettes, 26 with numerical classes**, some legacy entries intentionally unavailable or without numeric legends, not invented. Apply sky/scarlet to **export overlay chrome only**, never silently recolor real scientific rasters or replace actual class breaks.

The administrator's uploaded map image is used only as a faded, blurred decorative atmosphere in the standalone preview. Production must scope it to the **actual homepage whitespace only**, not map canvases or other product pages. Click sound is synthesized via browser Web Audio following a user gesture, default enabled with a visible mute control. Use subtle pressed transitions and `prefers-reduced-motion`, with no external audio CDN or added framework.

**Versioned code:** `ui_tabler_vnext_preview/index.html`, `vnext2.css`, `vnext2.js`, `palette-data.js`, `palettes.json`, `home-atmosphere.css` (embedded derivative supplied by administrator), `export_overlay_theme.css`, `tests/test_vnext2.py`. 23 local static/route/integrity tests passed. Chromium GUI E2E blocked locally even for localhost/file:// (`ERR_BLOCKED_BY_ADMINISTRATOR`), hosted private repo Actions may fail at provisioning. This preview and the guarded bridge are **not** a production release or evidence of live integration. Live index/htaccess and real map rendering need staged comparison and rollback.
