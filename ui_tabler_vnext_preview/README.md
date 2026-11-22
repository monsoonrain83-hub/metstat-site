# MetStat — Tabler-inspired UI Shell vNext (2026-11-22)

> **Status: ISOLATED, INTERACTIVE PREVIEW. NOT INSTALLED ON WTAFKIK.IR.**
> This package does **not** replace the production `index.html`, `.htaccess`, login/auth, NWP engines, isohyet solver, regional maps, or existing CSS/JS. No real weather forecast is rendered here. The cartographic background is explicitly schematic.

## Why this implementation

The live MetStat frontend is an older multi-page/HTML/JavaScript cPanel application. Replacing its large runtime with React/Next.js, adding multiple global CSS frameworks or embedding an external `@latest` CDN would introduce unacceptable regression and load/security risk. This self-hosted design shell therefore gives a **Tabler-first visual system** with plain CSS/JS and explicitly scoped classes, ready for code review and component-by-component integration.

Three user-supplied sources examined directly:

- `tabler-dev.zip`: source of **Tabler core v1.7.5**, cards, buttons, dropdowns, RTL palette/theme conventions, form density and dashboard navigation. Package is MIT. The distributed `tabler.min.css` is not inside the supplied source ZIP; **do not claim the runtime CSS is a compiled Tabler bundle**. This preview translates Tabler layout semantics to `ms-*` isolated CSS, preserving existing vendor styles.
- `ui-main.zip`: **shadcn/ui** (MIT) control patterns: semantic design tokens, visibly accessible focus, disclosure state, dropdown and switch semantics. Its React/Tailwind runtime is **not** injected into the legacy site.
- `magicui-main.zip`: **Magic UI** (MIT) restrained color/status pulses, hover expansion and micro-interaction patterns; animations honor `prefers-reduced-motion`. Its React/Framer dependencies are **not** shipped.

Self-contained CSS/JS combined ≈33 KB unminified, **zero runtime network/CDN calls**, zero server secrets, no third-party runtime dependency. Third-party provenance is documented in `THIRD_PARTY_NOTICES.md`.

## Explicit design acceptance contract

1. **Desktop-sized canvas on all devices:** min width 1180 CSS pixels; never one-column/mobile-card layout. On portrait devices the whole desktop canvas pans horizontally at native readable font sizes rather than shrinking to illegibility. Landscape sees more of it. Fullscreen uses a scrollable fixed viewport with an internal min-width map, so model and tool rails never overlap.
2. One-row header with top-level pages; logo and account actions on opposite sides, no double-height header even on mobile.
3. Five dropdowns **in a single row above the map**, always present and ordered continent → region → country → province/state → county. Unverified boundaries, especially incomplete Iranian county datasets, **must not perform false zoom**. The preview does not pretend to have complete boundary data.
4. Forecast controls together: product kind (daily/weekly/monthly/seasonal/ensemble), model, primary/secondary parameters, run and valid lead. ECMWF and GFS appear **once per logical model**. This shell does not choose data/resolution without per-frame backend provenance.
5. Map appearance controls together: county lines, towns, villages, roads, rivers, lakes, labels, line thickness, label sizes, wind animation/speed. Panel opens via icon; outside click and Escape close it. Changes dispatch typed `metstat:ui-action` events without rewriting map data.
6. **Latest user specification supersedes older r205 horizontal model-chip behavior:** original colored model chips are **vertical at the right corner inside the map**, including fullscreen, with ready=green, missing=red, partial=blue and updating=pulsing amber. The demo's colored statuses are explicitly illustrative; production colors must come from validated manifest status. **No duplicate `#fsMods` node or competing r205 horizontal script after integration.**
7. **Left inside map:** zoom in, zoom out, full extent, then **refresh**, ordered top-to-bottom. Icon-only collapsed controls expand on mouse hover/focus or tap with a 180–240ms transition, with labels and `aria-*`. Reduced-motion support disables visual effects.
8. All sections use the same layout tokens, map sizes, headings, control sizes and palette. Main selection targets are ≈40px tall; CSS buttons/tooltip expand without changing the grid size.
9. All routes are explicit and separately addressable, e.g. `/monitoring-forecast/weather-models`, `/monitoring-forecast/weather-models/weekly`. Local preview `preview_server.py` can serve all 12 canonical paths directly; **the real Apache and auth routes have NOT been modified.**
10. Security: no `innerHTML`/`eval`, zero HTTP calls in preview, explicit route allowlist and conservative CSP, no public administrative files, no automatic deployment or auth bypass.

## Run locally

```sh
cd metstat-tabler-v1
python preview_server.py --port 8765
# Browse: http://127.0.0.1:8765/monitoring-forecast/weather-models
```

Run the smoke, static quality and HTTP deep-link tests:

```sh
python -m unittest discover -s tests -p 'test_*.py' -v
node --check app.js
```

**Known environment constraint:** automation Chromium in the assistant's execution environment is controlled by an administrator's `URLBlocklist: ["*"]`; page navigation fails with `ERR_BLOCKED_BY_ADMINISTRATOR`. No visual/browser touch QA claim is made. A normal non-managed Chromium/Chrome or Playwright CI runner must validate the desktop, phone landscape and phone portrait layouts before shipping. The Python/DOM/JS/CSS/HTTP tests can run locally without Chromium.

## Integration gate: add to the current production site without regression

1. Obtain **read-only** fresh `index.html`, `.htaccess`, `assets/metstat_core_v105.js`, authentication endpoints, all existing live stylesheets/scripts and `version.json` from the **current cPanel DocumentRoot**, not `site_src.zip` or an older recovery archive. Compute SHA256 and keep offsite backups and a reversible manifest.
2. Audit the existing canonical DOM: identify actual map containers, fullscreen `#nvFs`, existing original `#fsMods`, model/run/lead selectors, layers and controls, routing logic and auth lifecycle. Check exact active version and whether r205 horizontal relocation is active. The current live HTML is **not available inside this design package**. A selector cannot be safely invented.
3. Integrate *in place*, via guarded opt-in under a single root, first add `ms-` theme tokens and matched Tabler semantics, then **move (never clone)** the original DOM nodes into the new rail/toolbar; preserve original event listeners, hidden inputs, IDs and form states. If a required original node is missing, **fail closed, preserve the old UI**. Do not mount an alternative map or a second set of duplicate model buttons.
4. Bind `metstat:ui-action` to actual existing map events: `zoom`, `full-extent`, `refresh`, `forecast-apply`, `geo-selection`, `layer-toggle`, `map-display`; read model statuses and allowed leads from a verified **same-cycle per-field manifest**, not the demo values. Do not let a +360h visible option imply an unavailable frame. For a real product the demo `NO MODEL DATA` overlay is removed only after successful map engine mount.
5. Ensure each new URL is resolved on a **direct HTTP load and reload** through the currently active login/auth+front-controller mechanism. Test anonymous redirect, authenticated navigation, logout, reload, back/forward, Persian text, duplicate assets and legacy URLs. Avoid blanket `RewriteRule ^.* /index.html` that would override `/online`, `/auth`, tools, assets and secure PHP endpoints.
6. Do **not** delete old URLs immediately. For `/monitoring-forecast/weather-models/online-maps` keep a temporary compatible alias while testing. Only after canonical authenticated routes return HTTP 200 and browser history works, issue deliberate **301** redirects for retired public paths; preserve private/query/API URLs. See `routes.json` for explicit paths.
7. Run automated UI tests on 1440×900 and 1920×1080 desktop; 844×390 landscape and 390×844 portrait; browser zoom 80%/100%/125%; pointer hover, touch pointer, keyboard Tab/Escape; RTL/LTR, fullscreen transitions, menus above map, rail bounds, map overlays; verify *no overlaps, clipping, horizontal jumps or JS exceptions*. Validate with actual NWP/ensemble/isohyet/station/flash-flood pages, not just the demo.
8. Roll out with a versioned asset manifest, same-origin self-hosted files, file hash preflight, authentication pass, explicit admin approval and rollback. Keep the last working cPanel release until the new system is visibly healthy.

## Canonical layout migration note

The prior master requirements section 8.2 and r205 wanted the original model chips **horizontal at the fullscreen top**. The administrator's newer request of 2026-11-22 explicitly changes that requirement to **vertical on the right inside the map** for the new global UI. This is a deliberate spec amendment, not permission to leave both layouts or two `#fsMods` elements. Any legacy r205 CSS/JS relocation must be retired or conditionally disabled *only after* new UI adapter deployment and visual QA.

## Required next work (not represented as completed)

- Read latest private live cPanel source; implement a tested in-place adapter for actual `#nvFs`, `#fsMods` and map engine without duplicates, including real county/roads/rivers data layers.
- Replace illustrative colored states with real manifest availability, preserve all scientific data and DEM correction.
- Deploy a canary to a non-production path with exact live asset hashes, visual browser QA and route-level tests.
- Only then replace the main site shell and migrate old URLs, retaining rollback.