# MetStat existing-site vs full-site r3 simulation — capability and provenance gap audit

**Comparison scope:** the administrator's earlier 6+ MB HTML snapshot `MetStat_P18_COMPLETE_LAYOUT_TEST.html` (11 November 2026), today's publicly reachable site homepage for product names, `METSTAT_MASTER_REQUIREMENTS_1405-08-30_v1.md` and later administrator instructions (including 22 Nov 2026). **The latest real cPanel webroot, runtime API, authentication, PHP handlers and deployed `.htaccess` have NOT been inspected fully; live feature parity cannot be certified.** `route_catalog.json` records provenance per page; proposed URLs are **not guaranteed existing live routes**.

| Section / feature | Previous sources | r3 mock UI | Real integration gap / status |
|---|---|---|---|
| One-row global header, cascading navigation, shared spacing/typography and theme | New administrator requirement | All 43 mock routes share one shell and five top-level groups | Production navigational IDs, permission/active-page states, old-to-new mapping and accurate routing require staged migration |
| Full-width desktop and landscape phone / portrait with user pinch | New requirement | Fills viewport, minimum desktop-like width for portrait, user-scalable; browser layout tests at 5 viewports | Actual Android pinch zoom, landscape orientation changes and device safe-area need physical-device testing |
| Five-dependent areas and zoom region controls | Master requirement | UI selectors and labeled map mock | True province/county boundaries, dependent choice lists and zoom extents require verified GIS catalog and map library |
| Daily ECMWF/GFS/ICON/GEM/UKMO and other models | Master requirement | Full model names and flags in right panel; compact right-map flags/icons; static mock statuses | No real NWP source manifest, run, level, valid time, 9/13/28 km resolution mapping or true green/red/blue statuses in preview |
| Weekly/monthly/seasonal/ensemble products | Master requirement | Independent product choices and distinguishable model short names in compact rail | Actual 7-model monthly/seasonal inventory, SEAS5 updates, calibrated anomalies, precise ensemble membership, validity/lead availability |
| Custom multi-model workflow | Administrator's latest request | Dedicated switching panel, member weights, generated illustration, return preserving forecast UI state | Scientific blending, weight normalization per real input, common cycle, grids, masking, unit handling, provenance and actual output absent |
| Forecast timeline | Latest requirement | Compact previous/next/play and time range UI | Available hours from actual manifest, variable frame intervals and cache/data preload missing |
| Map layers, line widths, label sizes, wind animation | Latest requirement | Icon-only layer controls, display setting panel and demo | True GeoJSON/vector/raster layer bindings, line-width rerendering, labeling, wind particle engine and legends missing |
| Palette gallery | Old site `MT_PALS`, `MT_PAL_EDGES`, `MT_PAL_LIB` | 41 original palettes, 26 with verified numerical break arrays; per-parameter preview chips | Actual raster style binding and scientific units, some omitted incomplete legacy palette legend ticks, cross-parameter constraints need audit |
| PNG / GIF save | Older site popup and user requirement | Lower-left Save, PNG UI demo, GIF settings modal | High-resolution tiled map screenshot and encoded GIF frames are NOT produced; output worker/memory/host budget and file correctness need implementation |
| Rainfall isohyet and station matching | Old site, historic station XLSX discussions | Distinct UI routes for isohyet and matching | Actual station database resolver, text parsing, interpolation and Excel input/output not connected |
| WeatherBELL, weather.us, TropicalTidbits, weathermodels, universal map, weighted composite | Existing homepage menus | Separate tool pages and context-appropriate demo controls | Existing upload workflows, georeferencing, crop, color restoration, layering and export algorithms are not cloned |
| DEM/orographic, convection, lightning-density, severe weather | Old site and requirements | Individual UI pages | Input rasters, scientific calculations, formats, caching and provenance missing |
| Realtime stations, radar/satellite, lightning, alerts | Existing homepage and requests | Dedicated pages | API/station observations, latency and operational alert thresholds not present |
| Synoptic chart, jet stream, teleconnections | User instructions | Dedicated subpages | Full interactive map/plot product data and scientific axes missing |
| Climate indices, atlas, drought, CMIP6, outlook | Homepage and master requirements | Individual page shells | Actual chart datasets, plot styling and statistical processing not present |
| Flash flood probability and verification/IRIMO bulletins | User requirements | Distinct preview pages | DEM, basin layers, hazard formula, observed/reference data, metrics and upload of real bulletin maps missing |
| Public/canonical URL migration | Administrator's requirement | 43 mock deep links return 200 via local preview server; unexpected routes return 404 | Live `wtafkik.ir` 404/auth/old aliases/301/SSL/HTAccess/CDN need separate end-to-end; never apply generic rewrite blindly |
| Map product theme and background photo | User supplied images | Blue/white/red UI; admin's image blurred only as decorative background on mock homepage | Real map export chrome and actual homepage rendering need staged wiring; never recolor scientific raster or render background under forecast map |

## Evidentiary boundaries

- Scientific values/forecast fields in preview are **illustrative placeholders only**, never model runs or operational data.
- The route list is a **design information architecture** consolidating master requirements and known past widgets. It does not establish that all proposed pages are currently installed or that this redesign is already deployed.
- The colorbar palette data is read from a historical administrator-provided site copy. Production must compare it with the current palette library at release time to prevent user-defined palettes being lost.
- Fullscreen/mobile tests use simulated Chromium viewports (not real touchscreen). Continuous rendering, accessibility with assistive tech, authenticated links, performance on the host and precision of generated maps still need acceptance.
- Preserve previous working functions and scientific algorithms. Mark features **not simulated** rather than silently deleting them when replacing the old front end.

## Safe next migration gate

1. Fetch exact latest live `index.html`, `.htaccess`, relevant JS/CSS, current route front controller and metadata; hash/backup.
2. Build a real feature-to-event-handler inventory (selector, source, destination, persistent state) for **every** site page against the 43-page simulation map. Flag unrepresented functions; do not replace the site wholesale.
3. Connect one integration adapter with progressive opt-in, preserve existing model-status DOM nodes and event listeners. Handle the forecast ↔ custom multi-model state machine without remounting map canvases unnecessarily.
4. Stage and test all screens at four widths + device rotation and zoom; visual diff screenshots + keyboard/touch + screen-reader naming + contrast; ensure zero new 404, CSRF/authorization regressions or asset breakage.
5. Conduct authenticated cPanel canary deployment, live meteorological data validation, compare real output products, monitor logs and revert if acceptance fails.