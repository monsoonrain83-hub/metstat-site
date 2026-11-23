# MetStat vNext r3 — Entire-site interactive UI simulation

**Date:** 2026-11-22 (1405/09/01). **Status: INDEPENDENT PREVIEW, NOT A PRODUCTION UPDATE.**

The simulation is designed for visual/interaction review and includes 43 distinct mock paths (5 top-level groups). It does **not** process or display actual meteorological data, publish products, authenticate users, or create forecast GIFs. Model availability signals on the mock map are illustrative. Read the UI caveats before comparing against a live forecaster.

## Open

- **Simplest:** Open `MetStat_vNext_r3_ALL_PAGES_INTERACTIVE_OFFLINE.html` in a modern browser (desktop Chrome/Edge recommended; Android browser/HTML Viewer can work). It is one self-contained file without network dependencies.
- To use the distinct HTTP simulation URLs locally, execute `python preview_server.py --port 8063`, then browse to `http://127.0.0.1:8063/` on the SAME device. The server only binds localhost and intentionally returns 404 for unknown routes. These are **not** claims about `wtafkik.ir`.
- To rebuild the independent file: `python build_offline.py` from this directory. The bundle embeds only local HTML/CSS/JS, a derivative of the administrator's submitted background image, and the previously supplied site palette colors.

## Specific interaction flows

1. Header: only 5 top-level menus including Home; click to open cascading routes; choose any route and its own sidebar and simulated map/table/chart controls appear.
2. Forecast: select daily/weekly/monthly/seasonal/ensemble; choose an actual model name or acronym, parameter hierarchy, run and time steps. Model icons remain compact on the map (daily uses a small identifier/flag; longer-range has distinguishable short model codes); right menu includes full names and flags.
3. Multi-model: click **مولتی‌مدل سفارشی** below right forecast controls; the forecast controls hide and the alternative multigroup settings and overlay canvas appear. Change member selections/weights and generate a **visual illustration**. Click **مدل‌های هواشناسی** to restore the preserved forecast choices and forecast canvas. No algorithm/data combination is performed by this preview.
4. Map: icon-only plus/minus, full extent, refresh and layer controls; save button at lower-left opens the PNG/GIF dialog; GIF opens a second modal for the range/fps/duration/loop. Exported PNG is watermarked UI DEMO; **GIF file rendering is not implemented**.
5. Palette: wide selector presents the original saved MetStat palette colors and (only where known) their corresponding numeric classes. This UI does not recolor the scientific raster or imply an unavailable color table exists.
6. Landscape fills the visible desktop-like workspace; portrait stays desktop-oriented with horizontal scrolling. Browser pinch zoom is permitted (viewport user-scalable yes / touch-action pinch-zoom); physical mobile gesture behavior still needs actual-device QA.
7. Short click-sound demo is OFF by default. Activate deliberately using the sound button; it requires a user gesture and no remote audio files.

## Testing / acceptance

```bash
python -m unittest discover -s tests -p test_r3.py -v
python -u tests/browser_qa.py
python -u tests/browser_all_routes.py
```

At time of writing: 24 local structural/route/security checks PASS; Chromium tests PASS against **in-memory DOM** at 1920×1080, 1440×900, 1280×720, 844×390 and 390×844, checking custom/forecast switching, save/GIF/layers controls and all 43 navigation targets. Managed network/browser policy blocks normal `file://`/localhost Chromium requests in the test sandbox; in-memory injection therefore does not prove normal URL/Android browser behavior.

**Never upload this directory or the offline HTML over production `index.html`, `htaccess` or `/assets/`.** This preview is only for design review. Integration requires a separate staged adapter against the newest live front controller, map engine and existing widgets, per-page feature parity and user approval, regression tests, backups, and rollback.

See `AUDIT_GAP_MATRIX.md` for functionality coverage and missing live features.