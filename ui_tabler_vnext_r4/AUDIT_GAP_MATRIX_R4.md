# MetStat r4: review of old-site feature families against the simulation

Sources used: administrator master requirements `METSTAT_MASTER_REQUIREMENTS_1405-08-30_v1.md`; the user's historic HTML `MetStat_P18_COMPLETE_LAYOUT_TEST.html`, including its `NAVI` menu declarations, r97 account-panel UI and fullscreen meteorological-drawing controls; the previous r3 simulator; and specific follow-up instructions in this chat.

**Caution:** The historic HTML is a snapshot, not the hash-verified current cPanel release. Grouping is based on documented and inspectable historical labels, while proposed nested paths and admin route names remain subject to the operator's acceptance. All 63 entries in `route_catalog.json` retain `route_verified_live=false`.

| Original or requested family | r3 state | r4 review state | Still missing before live integration |
|---|---|---|---|
| Main nav family | One-level/incorrect page assignments | Five historical top-level families; nested click-open menu hierarchy; routes annotated parent/source | Verify latest deployed hierarchy, exact labels, route redirects, direct 200 reload |
| Forecast daily/weekly/monthly/seasonal/ensemble | Simulation | Preserved; discrete right-hand model rail and palette selector | Live ECMWF/GFS data and available-run manifests, calibrated values, live map engine |
| Custom multi-model UI | Simulation toggle | Preserved in r4; right sidebar swaps without discarding forecast selection | True NWP data mixing/weighting, genuine map render, fail-safe cancellation |
| Account navigation and roles | Absent | Header account dropdown, account overview, login, registration, favorites, profile/password, admin and monthly station approval screen variants. Disabled fields and explicit demo roles | Actual secure auth, permissions, CSRF, admin functions, account persistence |
| Fullscreen drawing tools | Absent | Overlay: freehand/straight/dashed lines, arrow, cold/warm/occluded/stationary synoptic fronts, rectangle/circle/polygon, points/text/H/L, erase, width/color, undo/redo and fullscreen | Georeferencing, GIS layer serialization, calibration of geodesic ruler, real export and persistence |
| Layer menu and map tools | Present as simplified UI | Preserved, icon-only left toolbar and separate drawing pen | Real layer boundaries, labels and line settings from original GIS engine |
| Save/output dialogs | Demo PNG and GIF settings | Preserved from r3 | Production true-resolution PNG export; actual GIF encoder by lead and selected area |
| Meteorological applications | Generic cards | Dedicated routes (agriculture, mountain, aviation, etc.) and source-categorized controls | Real domain calculators and dataset integrations per original module |
| Analysis, stations, climate and tools | Partial name inventory | 63 standalone route identities across monitoring, applications, synoptic, toolbox, climate and account; source provenance per page | Individual module functionality cannot be inferred from old filenames; run on latest live source and validate with admin |
| Layout / portrait / landscape | Landscape sidebar clipped at 844px | Two-column 844px fully fitted; 390px uses horizontal scrolling without mobile one-column; 1920/1440/1280 also tested | Physical phone tap/pinch, focus navigation and production CSS conflicts |

**QA evidence:** 16 Python/HTTP structural test cases (including checking all 63 direct demo paths) passed; headless Chromium exercised the 5 viewports, auth-menu navigation in demo, cold-front draw, undo/redo, text label, map fullscreen and landscape toolbar without page errors. Actual cPanel redirects, real auth, accessible control contrast on every screen, and scientific data export have **not** been validated. Design tokens are blue `#399FD4`, white `#F8F9FD`, scarlet `#DC1937`; the original model-update status color semantics stay logically independent.

**Release decision:** UI prototype available for operator review only. Do not merge PR to a deployed branch or upload this `index.html` to live webroot before a separately validated integration build and rollback bundle.