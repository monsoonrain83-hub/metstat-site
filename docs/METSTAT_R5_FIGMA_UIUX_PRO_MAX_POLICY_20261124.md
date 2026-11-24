# MetStat — R5 is the canonical visual source; Figma + UI UX Pro Max QA policy

**2026-11-24. Administrator instruction. Status: spec + test tool in draft PR #27, not a cPanel release.**

## The authoritative artifact

Administrator-uploaded `OPEN_METSTAT_R5_ANDROID_FIXED(1).html`, SHA256
`2792e674660f07135acb91f6cbf92f8740f4c9ff8c073e94767927b1c8dbadf9`.
Treat the artifact as **the visual, navigation, interaction and geometry reference**. Do not treat it as a source of actual meteorological raster/forecast/model data. Do not overwrite operational `index.html` with this offline R5 demo.

This supersedes any tempting redesign towards R7/R9 or the generic advice to turn mobile into a one-column app. Existing R7/R9 host owners are **implementation details**, not alternative visual standards; migrate the existing owners toward R5, preserving all functioning menus, weather engines, GIS layers, maps and route addresses.

## Tested, not guessed: four real Chromium R5 snapshots

| Viewport | Original right sidebar | Map width | Header | Two columns |
| --- | --- | --- | --- | --- |
| 1440×900 | 328px | 1082px | 64px | Yes |
| 960×720 | 230px | 718px | 64px | Yes |
| 844×390 | 230px | 602px | 44px | Yes |
| 390×844 | 305px | 636px | 64px | Yes, but map starts outside visible left edge |

All four R5 fixture loads: **7** actual top-level nav buttons, **5** select elements (`geoContinent`, `geoRegion`, `geoCountry`, `geoProvince`, `geoCounty`), **7** actual model-status controls, FA/RTL, no JS page errors.
Colors: `--sky:#399FD4`, `--paper:#F8F9FD`, `--scarlet:#DC1937`.

**Known R5 issue:** at 390px portrait the unmodified file's map is partially clipped and `document.documentElement.scrollWidth` does not expose the full 960px canvas. Stage31 separately has a fixed *preview* restoring horizontal access without changing the desktop two-column composition. This known limitation must not be mistaken for successful touch UX on Android.

## Integrate GitHub UI UX Pro Max without overriding R5

Source library: [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill), exact upstream `.claude/skills/ui-ux-pro-max/SKILL.md` and `references/quick-reference.md` consulted 2026-11-24. Apply its **testable** controls, not an unrelated aesthetic theme:

- AA text contrast for text, distinguishable statuses beyond color, visible keyboard focus, named icon-only buttons, real select labels and tab order; no disabled controls pretending to work.
- Preserve actual document scroll accessibility for 390px portrait without single-column stacking; in landscape keep the two columns and let each necessary panel scroll independently.
- Protect controls from collision: original colored fullscreen model buttons must be **moved as the same DOM nodes** to one horizontal row at the top, not copied into a second control family. Map, zoom, palette, downloads and 5 geographic selectors must be reachable.
- Respect reduced motion, readable focus/feedback, safe-area insets, real loading/error status, performance and no added layout-thrashing polling.
- Document deviations from generic Pro Max guidance: the owner's **desktop-style everywhere** policy overrides mobile-first/no-horizontal-scroll and 16px-phone-body recommendations where these would disrupt the fixed R5 information architecture. Preserve R5 palette, header order and menu taxonomy.

**No blanket "UI UX Pro Max = error free" assertion:** these are QA criteria. Pixel screenshot comparison, browser interaction, JavaScript regression, live PHP/API and genuine weather layers remain separate acceptance checks.

## Figma connector status

Prior MetStat design file key: `h9lb9hKlGLTJ5yeqXtUnix`. The Figma connector's `create_session` call returned **no edit access** on 2026-11-24. The file's nodes/screens/components were **not read**; no Figma edits were made. Do not invent Figma-matched colors or claim current UI was synced. The file owner needs to grant the connected Figma identity **Editor** rights for connector operations. Once access exists, inspect the existing screen/component names, compare against canonical uploaded R5, and treat R5 as authority when Figma historical work differs.

## Repeatable acceptance and guardrail

- `specs/R5_CANONICAL_VISUAL_GOLDEN_20261124.json`: canonical source SHA, four real viewport dimensions, R5 colors, five geographic IDs and seven original controls, with explicit user-exception documentation.
- `tools/r5_browser_golden_capture.py`: **read-only**, takes the exact administrator-supplied local R5 file, draws four isolated Chromium viewports, writes real PNG screenshots and the measured JSON report. Requires local Python Playwright and Chromium; does **not** access host or Figma.
- `tools/r5_uiux_report_gate.py`: source-pinned validation of the output report (palette, geometry, original controls, RTL, no browser errors).
- `tests/test_r5_uiux_report_gate.py`: negative tests for unexpected model duplication, wrong layout, missing geography, recoloring, missing or duplicated viewport, failed JS, unknown R5 SHA. The GitHub Actions R5 workflow runs these unit tests. This CI **does not** capture R5 screenshots by itself without the private administrator reference file.

After obtaining the file in an authorized local workspace, run:

```bash
python -m tools.r5_browser_golden_capture "OPEN_METSTAT_R5_ANDROID_FIXED(1).html" --out ./r5-evidence
python -m tools.r5_uiux_report_gate ./r5-evidence/R5_GOLDEN_BROWSER_REPORT.json
python -m unittest discover -s tests -p 'test_r5_*.py'
```

**Release acceptance for a change to the site (not yet automatic):** baseline screenshot comparison (not just R5 self-test), FA/EN, portrait/landscape, fullscreen map and original model controls, no collisions, accessibility, all site routes/no 404, actual manifest and model provenance, isohyet/toolbox/verification/stations regressions, security and full rollback. Do not merge this draft PR or replace the live index before those pass.

## Exact scope / audit honesty

The present stage delivers source ownership, an immutable R5 golden specification and tests; it **does not** claim pixel-perfect migration of the 6.4MB active host HTML to R5, Figma access, live NWP integration, production deployment or server health.
