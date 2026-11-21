# MetStat — Glass Desktop Atlas / audited recovery plan (2026-11-22)

> **Status: DESIGN / OFFLINE RECOVERY ONLY — NOT INSTALLED ON LIVE HOST.**  
> Source-of-truth: `docs/METSTAT_MASTER_REQUIREMENTS_1405-08-30_v1.md` in NWP, plus user-supplied `backup host.zip` (2026-11-21) and archived `index(20261121-142945).html`.  
> Never advertise successful production release before live authenticated QA.

## Production incident and non-negotiable gates

1. Replacing the complete 6.3MB HTML page with r207 disrupted authentication and was followed by 404 incidents; selective cPanel rollback to 19-Nov restored service but lost later UI/nav changes. A route-only `.htaccess` edit was later reported to fix the URL issue. **Do not overwrite the currently working `index.html`, `.htaccess`, `auth.php`, databases, or FTP deployment paths from archived snapshots.**
2. Obtain read-only current `index.html` and active `.htaccess` from the actual cPanel Document Root; record SHA256 and effective PHP auth endpoint. Compare *three-way*: current live, last known functional pre-incident, requested change. If current live cannot be verified, changes remain review-only.
3. Preserve the normal authenticated user path from `/login` to `/monitoring-forecast/`; direct load/reload of the latter must return HTTP 200 rather than a 404. Test authenticated and anonymous routes, logout, session refresh, all menus and Persian/English.
4. No automatic FTP deployment for the private site unless an administrator explicitly authorizes and live release gates pass. Backup outside web root; prepare a single complete installer-free artifact ONLY after validation; retain one-click rollback. NEVER expose `admin/private/`, debug logs, installer PHP or credentials publicly.
5. Tests must run against the real complete HTML, not a mock of `nvrBuild()`. Local/CI pass != live host pass.

## Confirmed inventory from user's backup

- Full `index.html` and `index_new.html`: identical **6,365,131 bytes** (archived, not proof of current active page); differs from another 21-Nov snapshot by a `<base href="/">` line.
- `assets.zip`: **69 ZIP entries**; among them `metstat_r96_desktop_shell.css`, `metstat_r97_layout.css`, `metstat_r120_ux.css`, `metstat_r121_fullscreen.css`, `metstat_map_ui_r201.css/js`, `metstat_geo_r203.css/js`, `metstat_original_model_chips_horizontal.css/js`, `metstat_core_v105.js`, various overlay/UI helpers.
- `station_isohyet_v26.html`: **78,610 bytes**; `station_match_v39.js`: **11,366 bytes**. Their mere existence does not prove that today's active isohyet UI works. The archived full `index.html` contains **zero references to `isohyet`**; restore navigation separately from preserving the backend.
- `data.zip`: observation/OSM/flood reference snapshots. `metstat_data.zip`: data index and station registry.
- `admin.zip`: 68 entries, including `admin/private/config.json`; **sensitive material**; never extract blindly into public web root.
- An archived `htaccess` has explicit nested paths such as `monitoring-forecast/weather-models` / `isohyet-map`, but no base route `monitoring-forecast/`; user reports route issue now corrected on host. Do not reapply archived rewrite rules.

## UI policy: ONE desktop experience on every display

**No single-column mobile version.** Keep desktop logical viewport/design canvas width ~1366–1440px (configurable design tokens), with an outer horizontal scroll container on narrow phones and full pointer/touch handling. HTML viewport meta must remain accessible: do not disable pinch zoom, shrink buttons to 8px, or use `user-scalable=no`.

- Premium restrained glass surfaces with `backdrop-filter: blur(12px)` where supported; opaque fallback, minimal translucency over data, strong contrast (WCAG AA target), reduced-motion fallback. Prefer CSS transitions (120–220ms) for hover/open/close; avoid expensive full-screen blur/continuous animation during map pan/zoom.
- Preserve **only existing** original model-chip group; do not clone/recreate the colored ECMWF/GFS/GEM/ICON/UKMO buttons. Logical ECMWF and GFS eventually become single model selectors per master MD. Each map frame must show native source resolution without guessing.
- Put FIVE cascading geography selectors in exactly ONE horizontal row ABOVE the map: `World / Continent -> Region -> Country -> Province -> County`. Support all 31 provinces when verified; county options require actual geometry, never name-only zoom. Language defaults as documented; click-outside closes dropdowns.
- Migrate (reparent) the existing border, overlay, label, capital, city/road/rivers visibility controls to the thin map toolbar, preserving original event handlers and state. Color settings immediately below legend; fine settings behind a real gear. No duplicate controls above/below canvas.
- Layout: app header/navigation; five selectors bar; fixed width tools sidebar (desktop), map canvas with stable aspect and valid-extent label, timeline directly below, legend+metadata below timeline. Existing model panel, weather toolbox, live station map, verification, flash-flood, charts must remain navigable.
- If selected map's actual metadata/coverage does not contain new extent, show explicit unavailable feedback; NEVER reuse ME or Iran image as China/world.
- On mobile: intentionally scroll horizontally to use same DESKTOP interface, but touch controls remain >=44 CSS px where feasible; two-finger pinch and map drag interactions must not be hijacked. No responsive breakpoint switching to stacked card view. Header/toolbar and map must not overlap.

## Figma (design proposal, NOT live code)

Editable design file: https://www.figma.com/design/Lv8bFV1IO28YuYvfzqPaPx
- Frame `METSTAT / GLASS ATLAS / 1440x900 DESKTOP-FIXED`, node `2:2`.
- Glass blue/graphite visual system, fixed control rail and sidebar, 5-step geography, timeline, colored model group and legend.
- Schematic map body is a **placeholder**, not a forecast/data product; all actual source map imagery and geographic overlays must be reused from the existing renderer during implementation.
- Actual project's embedded fonts `Ketab` and `Titr` are absent from Figma runtime; the draft uses available fonts and should be tuned to exact product typography once an available equivalent is selected.

## Xweather UI SDK research (NOT drop-in migration)

Documentation: https://www.xweather.com/docs/maps-ui-sdk — a React/TypeScript UI library based on React Context and MapsGL; modules: `MapsGLLayersControl`, `MapsGLTimelineControl`, `MapsGLSearchControl`, `DataViewer`, `Timeline`, `Fade`, `Slide`. Its getting-started example needs Xweather MapsGL credentials and a Mapbox public token. Review API licensing and terms before any production adoption.

Recommend deriving the UI interaction patterns (shared state, layered timeline, accessible controls) without replacing the site's PHP + JS + existing NWP map renderer, which would be a major rewrite, credential requirement and data migration with no proven benefit to native weather model content.

## Graphify: indexed repo limitations

Graphify queried 2026-11-22; authorized index currently lists:
- `monsoonrain83-hub/metstat-maps` (indexed ~2026-11-19, `nwp_maps.py`, `geo_layers.py`, `ens_maps.py`, `ec46_maps.py`, and workflows);
- `monsoonrain83-hub/weather-model-ensemble`;
- `monsoonrain83-hub/wtafkik` — **Android Kotlin map-overlay app**, not the website.
Graphify does **not** index the live `metstat-site` or main `metstat-nwp` repositories in its authorized workspace. Therefore code relationships observed there are historical context only, not instructions for replacing the live frontend. Use live private GitHub + host backup + master MD as implementation source.

## Restoration sequence and acceptance

1. P0: user confirms site URL routing, login, navigation stable on actual host; read current safe baseline and lock. If drift persists, stop.
2. Recover access to existing isohyet page: verify current `online/station_isohyet_v26.html`, `station_match_v39.js`, `online/api`, province station provider and UI entry; *do not regenerate station coordinates*. Add one existing menu link only after secure and relative routing checks.
3. Reinstate stable new UI controls incrementally from archived r97/r120/r121/r203; reconcile CSS conflicts first, delete duplicate stale overrides only after proof. Never blindly replay the old r201/r203 installers.
4. Actual multiresolution model priority, maps coverage, anomaly and seasonals in separate NWP PRs and CI, not CSS patch; ensure true provenance metadata and no false coverage.
5. Stop before live deploy until authenticated desktop browser 1440px and phone 384px tests pass at exact same logical desktop layout; test FA/EN and normal/fullscreen, 404 direct reload, panels, layer visibility, zoom, colorbar, time controls, login, API and rainfall map.
6. Stage checksum, backup, rollback, release gate and records in GitHub Issue #15. Mark **done** only with actual host evidence.

**Status this note:** design recovered/archived, Figma generated, offline evidence verified; no modifications to live host made.
