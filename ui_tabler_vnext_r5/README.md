# MetStat vNext r5 — Seven-section, source-aware UI preview (22 Nov 2026)

**Preview ONLY. Do not replace the production `index.html`, `.htaccess` or any backend on `wtafkik.ir`.**

## What was corrected

The seven first-level groups and all child pages are taken verbatim from the administrator's 22-Nov-2026 approved sitemap, instead of the previous inferred and misgrouped 63-page menu. `route_catalog.json` contains **68 distinct review paths** (including homepage, five period subroutes + custom multimodel, and seven account pages). The group count is seven; the user account is a separate header action, not an eighth content group.

The r4 navigation error came from `addLevel(drop, '', 0)` even though every child was indexed by its parent group root. r5 indexes children by `parent_path` and starts each dropdown from the actual group root path. Dropdowns are rendered in a body-level portal to avoid clipping behind the horizontal nav in narrow landscape windows. `data-route` links update the page title, right controls, and content, with file-hash routing in the offline HTML.

### UI behaviors now present in review build
- The same Tabler-inspired sky/white/scarlet shell, compact model **SVG image** flags/icons (no Unicode flag emoji), protected model-status colors, live-looking map explicitly marked `DEMO`, and separated hourly timeline.
- Browser-generated click sound now **on by default** after the first user gesture, one-tap mute, a brief pressed animation and reduced-motion support. No remote audio libraries or trackers.
- Forecast ↔ custom multimodel sidebar/content switching remains independently stateful; map fullscreen retains the synoptic drawing toolbar and its SVG annotations.
- New page-specific central workspace cards for all modules and actual child navigation. Relevant map pages retain a compact panel rather than obscuring the map and drawing surface.
- Ava Studio has **four** sections, linked from the corrected global hierarchy. Browser-native, local-only audio report playback using device speechSynthesis; photo filters with genuine PNG export; video upload, seek and range preview, genuine video-frame PNG export; and **rudimentary brightness-jump video scan** producing candidate times. Scanning is an **uncalibrated image-lightness heuristic** (not validated lightning AI); it can be triggered by camera movement, lights or codec artifacts. A professional detector has not been ported.

### What is NOT done
- Actual LightningLab Kotlin/Android `MediaCodec`, `Detector`, Jetpack Compose editing and TFLite engines are **not browser-ported**; no trained TFLite model was available in the GitHub source. No professional video export (trim setting is preview only), ML classification, authenticated accounts or cPanel integration.
- The 68 routes are review paths; their availability on the live site's original `.htaccess` has NOT been verified. Do not delete/redirect legacy URLs yet.
- Weather data, georeferenced map analysis, true forecast timeline availability, scientific computation and GIF rendering are not connected.
- Browser QA is done with Chromium in-memory DOM, because `file://` in the managed Chromium fails with `ERR_BLOCKED_BY_ADMINISTRATOR`. The standalone file was built with embedded styles/scripts but cannot be declared visually validated as an actual Android open-file UI without physical testing.

### Files
Open `MetStat_vNext_r5_ALL_PAGES_AVA_STUDIO_INTERACTIVE_OFFLINE.html` locally on a desktop browser or with a phone HTML file viewer. No web server is required. From the modular source, run `python build_offline.py` to rebuild the offline file, or `python preview_server.py --port 8065` on a local computer to test deep links in a normal browser.

For inspection: `index.html`, `styles.css`, `app.js`, `route-data.js`, `route_catalog.json`, `model-icons.js`, `account-r4.js`, `drawing-r4.js`, `feature-r5.js`, `ava-studio-r5.js`, `palettes.json`, `palette-data.js`, asset `assets/homepage_atmosphere.webp` and the tests.

No remote resources are fetched by the preview, user files are not uploaded, and account forms are mock-only. The model mini-icon graphics are locally authored SVG **preview marks**, not a claim of official ECMWF / NCEP logo licensing. Agency-owned official marks should be sourced and vetted before a production release.

## Independent LightningLab Web Core

`lightning-web-core.js` implements an independently testable **luminance-jump prototype kernel** for browser sampling with `meanLuma()` and `detectJumps()`; see `tests/test_lightning_web.cjs`. It is an explicitly non-scientific proof of the UI/dataflow, **not** the port of `Detector.kt`/`FlashAnalyzer.kt`. The same module is intended to be maintained in the LightningLab web branch and imported into MetStat only after reviewing compatible versions. No TFLite model weights are supplied.