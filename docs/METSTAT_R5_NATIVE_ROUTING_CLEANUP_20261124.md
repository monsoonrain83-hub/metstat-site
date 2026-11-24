# R5 single-owner route repair — applied meteorology duplicate pages (2026-11-24)

**Source:** exact administrator-uploaded operational host index.html SHA256
`7ff4bbfeb3b658ca8d36c6da3efa6bb83d7ffbca1cebcf8403ec2dff80f1c295`.
**Output candidate:** SHA256 `51df572c1cb0a044a803933a31d2d76f355e6cd5912f4ddf955abb468834dec6`.
**Status:** *not on cPanel*, no merge, no active-host SHA verification; all R5 source geometry and weather formulas unchanged.

## Defect proved, not assumed

There are two routing levels in the actual source: the original `GO` table invokes existing operational engines; the seven-group R5 navigation calls `navigate()`, which has its own set of linked native destinations. The R5 menu advertised `warn72`, `air` and `earthquake` but omitted them from the native dispatcher. Clicking them therefore created `#ms7Custom` containing the false-looking new page `'در انتظار ادغام ماژول اصلی'`, **even though the real `AP_TABS` already has `ex`, `exa` and `exq` with the actual application code**.

The base Stage41 screenshot of the apparent earthquake page and the real native `#apApp` climate warning/earthquake tab reproduce that mismatch. The second view was not another meteorological engine: it was a placeholder created by the R5 navigation owner. No map or weather-value generation had to be replaced.

## Root fix in existing owners, zero additive overlays

Edit precisely 2 original JS script blocks, with three surgical replacements:

1. Existing native GO handler: map `warn72:()=>openAP('ex')`, `air:()=>openAP('exa')`, `earthquake:()=>openAP('exq')` to their original `openAP` tabs. Do not create/clone HTML or move scientific callbacks.
2. R5 navigation `mapped` set recognizes those three native routes instead of creating `ms7Custom` placeholders.
3. Correct the R5 `'وضعیت کلی'` leaf: the native `ap` route always opens `openAP('ov')`, not whatever previous `AP.tab` happened to be.

The R5 menu taxonomy, all 7 top groups, 5 geography selectors, user-defined desktop-style 2-column layout, and all loaded page controller IDs are unchanged. **No new script tags, CSS rules, `!important`, observers, timers, or network calls.** Source non-script text is byte-identical; only script bodies 11 and 14 differ. This is a *replace-in-place* fix, not Stage42 CSS/script stacking.

## Real browser A/B evidence

Offline Chromium used the actual 6.5MB uploaded Stage41 original vs the 6.5MB candidate, and **real `map_layers.js` supplied in the uploaded `assets.zip`** (no fabricated physical arrays or fake model responses). Blocked external sites; no live API correctness claimed.

Tests: four viewports 1440×900, 960×720, 844×390, 390×844. For each, seven R5 route destinations `earthquake,warn72,air,ap,apm,apt,aph` plus actual mouse click on group/leaf R5 menu. Assert exact original AP tab, `#apApp` visible, `#ms7Custom` hidden, one application ID and main ID, seven nav groups, five geography selectors, zero page errors.

- **Stage41 baseline:** 16/32 passed, placeholder aliases fail in every viewport.
- **Repaired candidate:** 32/32 passed. The status page always returns to `ov`. No duplicated AP page or placeholder on any of these routes.
- All 19 original script sections pass `node --check`. Non-script markup, R5 layout and all scientific functions remain unchanged.
- True HTTP/cPanel routing, live Open-Meteo API, USGS earthquake data fetching and input response, Figma and physical mobile touch were not tested.

## Additional incomplete route audit (not fixed in this PR)

Static inspection of the 7-group R5 NAV found 51 leaf entries with 50 distinct internal slugs. **Another R5 menu leaf `convert-media` has neither a mapped engine nor a `MetStatR5Converters.render('convert-media')` implementation.** Stage22 conversions currently cover `convert-weather` and `convert-document` only. Do not paper over this by pointing it to an unrelated fake scientific/media converter; this remains explicitly open until a real implementation is approved.

The duplicate `cu` alias for Tropical Tidbits and 'other map websites' is a *shared existing browser/URL handler*, not a second independently created page. Other backend-dependent modules were not audited for live completeness.

## Deployment safety and rollback

- Replace ONLY the original `index.html` if **current** cPanel index SHA is exactly the Stage41 source SHA above and matching dependent assets are present. User may have hourly automation changing it: **unknown SHA => refuse overwrite**.
- The provided upload ZIP contains only `index.html`, not stale archived `assets/index.html`; no cPanel `.htaccess`, PHP, assets or NWP files are touched.
- Dedicated SHA-pinned Stage41 rollback ZIP restores original index.
- Do not deploy blindly to a public root, do not merge this stacked PR until Stage41 branch base and current host are checked.
- After authorized staging compare R5 screenshots, real API response, nav title, chart/map exports, isohyet, verification, all 7 groups, fullscreen and user changes; retain independent backup.

## Follow-on NWP without misleading global claims

The real NWP main `nwp_maps.py` has regional `BBOX=(-14,70,8,64)` and subregions; this cannot become global by simply renaming `region` or extending a dropdown. The repository also has a **separate** verified-grid global pipeline `global_nwp_stage.py` and `pack_global_products.py` for real ECMWF/GFS/GEM/ICON/UKMO fields, but the global-data artifact is not proven copied and integrated into the active hosted forecast viewer. New AIFS/AIGFS/CMA/JMA/GraphCast/KMA/WRF sources remain separate discovery/QC and must not be given false global/production-ready labels. Next acceptance is per-field native source, geometry, grid, cycle and valid-time QC, then actual upload to the same website and 404-free map display.
