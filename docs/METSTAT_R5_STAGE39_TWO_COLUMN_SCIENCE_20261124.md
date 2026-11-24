# MetStat R5 Stage39 — scientific right-controls / left-output two-column page layout

Date: 2026-11-24. Status: QA STAGING only. No production deployment or PR merge.

## Canonical source and acceptance

The exact administrator uploaded R5 HTML SHA256 2792e674660f07135acb91f6cbf92f8740f4c9ff8c073e94767927b1c8dbadf9 is the only visual source of truth. No R7 or R9 layout substitution. Preserve the *desktop-style two-column* page in all devices, using 328px right sidebar on desktop and the native R5 230px in 700–980px landscape. The portrait 390px uses a horizontally scrollable 960px two-column desktop canvas, not one column.

## Actual operational host source

Stage37 index SHA256 a6ee0843b29c300ec083ef0d7c636eb759ee4dd3eb9ea90d38079d5240243aa1 → Stage39 index SHA256 9dc68b50c2e8817e8e1b9996d8fd7d48f6defd016aca0a8cdd9a10c949d93e0e.

Stage39 edits only existing CSS owner ms9-desktop-r5-system plus TWO pre-existing three-column climate-atlas source rules (now two columns). Every inline JavaScript payload from Stage37 is preserved byte-for-byte, no new DOM control, ID, timer, observer, GIS or weather formula; !important count 1138→1138. Original floating accessibility button changes source CSS from right-over-controls to left of screen without changing handler.

## Scientific layout ownership by module

| Module | Right existing selection/actions | Left existing scientific result | Status |
| --- | --- | --- | --- |
| online NWP #onApp | model, parameter, run, geography | actual meteorological map & animation | original functioning viewer preserved |
| indices #ciMain | source, index, time period | chart, interpretation and index table | two-column CSS |
| satellite #saMain | satellite, channel, area | satellite/radar/lightning map | removed phantom outer 328px track |
| climate atlas #caApp | source station and temporal selection | station climate chart/map | original three-column rules removed; DB not verified |
| drought #drMain | index, drought method and valid period | map, statistics | offline database unavailable |
| monthly/seasonal #sfMain | model, variable, lead | actual forecast/anomaly products | grid fixed, offline climate asset unavailable |
| mountain #mtMain | area, peak, elevation, model | peaks ranking and data | uncertainty warning spans both |
| applied #apMain | application, parameter | scientific calculation | methodology warning spans both |
| flood #flMain | source, basin, hazard method | susceptibility/forecast | live hydrology not verified |
| observations #obMain | station, time, area controls | observation map/table | offline API unavailable |
| upper-air #labApp | source, coordinates, sounding/model | meteogram, diagnostics | native controls retained |
| synoptic #synApp | model, region, layers/contours | forecast-time synoptic map | native controls retained |
| previously two-column | #dsApp #cvApp #ltApp #wnApp #anAuto | unchanged native asides and main | no extra overlay |

Intentionally deactivated cqcApp remains inactive. No fabricated page or fake data.

## Proven browser and release checks

48 tests = 12 actual route modules × 4 Chromium viewport sizes (1440×900, 960×720, 844×390, 390×844), no JavaScript page errors. Seven nav groups and five geographical selectors retained. At 844 landscape, nav actual scrollWidth=clientWidth=623, whole document width=844, right native sidebar width=230. The 390 portrait retains scrollable 960px. Accessibility dialog opens/closes and FA→EN switches at each viewport. Real source images may be unavailable offline, and the tests do NOT establish live API or map product correctness.

Source pinned four-file release ZIP only for exact original host SHA256 a6d3c06bb3197671e2a7e1f3e2043b924a23ee35c76ca4f35ef9d1e1c66a90d8, or one-index release ZIP only for exact Stage37 SHA above. Manual original asset SHA checks required before overwrites. Separate source-specific rollback ZIPs. Reject any other active SHA (including Stages32–36 and hourly automation changes). Tools: tools/r5_stage39_host_gate.py and tests/test_r5_stage39_host_gate.py. Local QA ZIP includes reproducible patch script, metrics and screenshots, not to upload to host.

## Outstanding gates

Confirm LIVE cPanel source and assets before staging; actual valid model maps & image exports, menu interaction, FA/EN, all PHP routes/no404, stations, isohyet, toolbox, verification, security and rollback. Figma file inaccessible because connector reports no Editor access; no Figma design sync claimed. UI UX Pro Max recommendations are used as secondary QA guidance, never over R5.
