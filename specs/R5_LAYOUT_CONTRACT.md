# MetStat R5 — layout and release acceptance contract (Stage31)

**Date:** 2026-11-24. **Scope:** read-only R5 source audit and staged-site acceptance criteria. **Not deployed.**

## Source of truth and policy
- Actual 305,507-byte user reference: `OPEN_METSTAT_R5_ANDROID_FIXED(1).html`, title **MetStat Atlas — نسخه جامع r5**.
- Scientific/content policy: `docs/METSTAT_MASTER_REQUIREMENTS_1405-08-30_v1.md`; implementation roadmap: `docs/METSTAT_R5_UNIFIED_ROADMAP_20261123.md`.
- R5 is a **visual and navigation reference**, not a source of live meteorological fields. Do not replace the canonical Stage22 host index or archived isohyet, toolbox, verification, bulletin, GIS or station engines with the reference preview.
- The user's subsequent instruction for the site takes precedence over the preview: **retain desktop layout at every viewport**, preserve FA/EN, and move the **original** fullscreen model chips instead of cloning them.

## Exact reference DOM and tokens (inspected from original R5 file)
1. `div.app[data-mode]` has four direct region children in order: `header.header`, `div.title-strip`, `section.geo-bar`, `main.workspace`.
2. `.workspace` has direct `.sidebar` then `.content` in RTL; `.content` contains `.map-card` and `.map-stage`.
3. The *five real select IDs* are `geoContinent`, `geoRegion`, `geoCountry`, `geoProvince`, `geoCounty`. A geographic name without a real boundary must not invent map coverage.
4. `.header-tools` contains `#soundBtn`, `#uiSmaller`, `#uiBigger`. They are UX controls, not an authentication mechanism.
5. Base tokens: `--sky:#399FD4`, `--paper:#F8F9FD`, `--scarlet:#DC1937`, `--ink:#183b53`, `--muted:#577489`, `--bg:#eaf4fa`, `--line:#c2dfed`, `--panel-font:14px`.
6. Base desktop geometry: `.app { min-width: 960px }` and the primary `.workspace { grid-template-columns: 328px minmax(0,1fr) }`. R5 itself has later viewport-specific overrides.
7. No duplicate real DOM IDs; do not count textual ID strings inside inline scripts as actual duplicate DOM nodes.

## Measured reference geometry (Chromium local/offline)
The reference HTML was injected into an isolated Chromium page; this is **not** live-host QA. `390x844`: sidebar 305px and main content extends to x≈−564px; `844x390`: sidebar 230px; `960x720`: sidebar 230px; `1440x900`: sidebar 328px. No JavaScript page errors were observed in these four isolated initial-load fixtures.

**Important:** At 390px portrait, the original R5 viewport initially clips most of the map horizontally. This is not evidence of acceptable final UX. The live implementation must retain the desktop composition **and** provide accessible horizontal panning/zoom without invisible controls, map/menu overlap or a single-column substitution. The stage31 static gate is only the first of several acceptance gates.

## Executable acceptance
`python tools/r5_layout_contract.py path/to/R5-reference.html`

`python tools/r5_layout_contract.py path/to/MetStat_R5_STAGE29_SINGLE_FULLSCREEN_OWNER_STAGING.zip --expected-index-sha256 52c472adc7e2ff6f4b4ffb413595c914895d422cb8d8ab69a8349a8a3bd029eb`

- The first should pass **11/11 structural checks** for the exact reference.
- The second currently serves as a **gap report**; an R5 mismatch is not a deployment authorization. It is expected to fail until the staging site's canonical shell is genuinely integrated.
- ZIP read is limited to a single root `index.html`, 16MiB maximum, CRC verified, no extraction or overwrites. Optional exact SHA pin rejects unexpected index versions.
- Offline tests: `python -m unittest discover -s tests -p test_r5_layout_contract.py -v`.
- GitHub workflow `r5-stage31-layout-gate.yml` runs only the offline tests; **never** deploys.

## Stage31 controlled R5 portrait-access fix (preview only)
- Script: `tools/r5_preview_mobile_pan_patch.py`, requiring reference SHA-256 `2792e674660f07135acb91f6cbf92f8740f4c9ff8c073e94767927b1c8dbadf9`. It changes **exactly one existing CSS media rule**, adding `body{min-width:960px}` alongside the existing `.app{min-width:960px}` for portrait viewports narrower than 650px. It does not add any JavaScript, override layers, `!important`, duplicate control, or change a scientific field.
- New preview SHA-256: `917cffa487efade92232a792ec222a13de604e265b1691d7cf10ffe5b5b7c96b`. It is a separate `.html`, not a live site index or Stage29 bundle.
- Verified in isolated Chromium at 390x844: the document has 960px horizontal scrollable width; scrolling to the left reveals the map (`map-card.x` moves from about −564px to +6px). At 844x390, 960x720 and 1440x900, document width remains equal to viewport; no page errors in all four fixtures. Touch gesture usability on physical Android, map controls and actual NWP remain unverified.
- Rebuild command: `python tools/r5_preview_mobile_pan_patch.py 'OPEN_METSTAT_R5_ANDROID_FIXED(1).html' R5_PORTRAIT_PAN_PREVIEW.html`.
- Four additional offline tests check exact one-rule diff, non-changes to scripts/data, SHA drift and double application. Combined local total: **13 tests passed**.

## Remaining acceptance work (not yet claimed)
- Obtain the exact active Stage22 cPanel snapshot and the Stage29 ZIP as authorized raw bytes for reproducible staged patching; compare checksums before write.
- Map Stage29 IDs and CSS owners to the R5 geometry; fix **original** layout and control owners (no redundant CSS overrides/timers/observers), then run actual Chromium tests at four widths × FA/EN × normal/fullscreen.
- Verify original `#fsMods` moves/restores exactly once, five geo levels use real boundaries, menus close appropriately, map/legend/export handlers and all existing routes still work.
- Perform real NWP, security, cache, route and rollback checks before admin-authorized cPanel publication; static R5 parity alone is never Done.
