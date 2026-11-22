# MetStat vNext r4 — complete UI review simulator (22 Nov 2026)

**Review-only; not a cPanel release.** This is a standalone interactive MetStat shell based on the user master requirements and an earlier 6.4 MB actual site file (`MetStat_P18_COMPLETE_LAYOUT_TEST.html`). It has 63 unique mock routes, including seven account and administration views. Every route in `route_catalog.json` records historical provenance and is explicitly `route_verified_live: false`; this is NOT a promise the exact URL is already on production.

## Use
Open `MetStat_vNext_r4_ALL_PAGES_USER_DRAWING_INTERACTIVE_OFFLINE.html` in Chrome/Edge or an Android HTML-capable browser. No installation or web connection required. For direct mock-route reloads and navigation, run `python preview_server.py --port 8063` locally and open `http://127.0.0.1:8063/`. `python build_offline.py` regenerates the self-contained HTML.

## Complete visible UI in the simulator
Five nested top-level original-nav families (monitoring/forecast, applied meteorology, synoptic analysis, weather toolkit and climate analysis), a home dashboard, full-width desktop/landscape shell with portrait horizontal scroll, source-backed real historic colorbar swatches, right-hand vertical model status rail, period/model/parameter selectors, custom multi-model builder, demo Save PNG/GIF dialogs, and page-context-specific sidebars. Each demo screen identifies unsupported live-data actions.

The header user menu includes login, signup, favorites, profile/password, admin mode and monthly station data approval. Account forms are visual disabled examples; **no credentials are accepted, stored, transmitted or authenticated**. A demo user/admin role switch only changes the visual UI and never grants rights.

The map toolbar exposes a working **SVG drawing overlay** for line, dashed line, arrow, cold/warm/occluded/stationary weather fronts with appropriate repeated symbols, ruler (**screen pixels only**, no geodetic units), polygon/circle/rectangle, freehand, text, H/L centers, eraser, color, width, undo and redo. To draw: select tool using the pen icon, close the floating selector, drag on the map. All drawings exist **only in this preview's memory**; they do not alter scientific raster sources or the actual MetStat editor.

## Tests, limitations and gaps
`python -m unittest discover -s tests -p test_r4.py -v` checks catalog, names, JS syntax, account guard, drawing shapes, palette integrity, all 63 direct server routes, aliases and 404s. `python tests/browser_r4.py` uses local headless Chromium to exercise real menu navigation, account routes, draw cold-front using mouse, undo/redo, text dialog, full screen, and viewports 1920×1080, 1440×900, 1280×720, 844×390 and 390×844. Results and screenshots are located under `tests/`.

**Not yet working:** real accounts and roles, model-forecast data, meteorological calculations or multi-model composites, georeferenced line/ruler distance, physical Android pinch gesture verification, server-side PNG/GIF rendering, cPanel production URLs or live login/auth. For detailed old-to-new comparison, review `AUDIT_GAP_MATRIX_R4.md`. Never overwrite the existing site's `index.html` or `.htaccess` with this preview.