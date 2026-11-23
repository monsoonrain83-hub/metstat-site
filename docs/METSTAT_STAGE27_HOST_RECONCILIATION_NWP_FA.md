# MetStat Stage 27 — Host archive reconciliation and parallel NWP work
Date: 2026-11-23 (Iran local); status: **audit + NWP staging only**, not a live deployment.

## Deployment baseline — do not regress
- Per administrator: the `index.html` currently uploaded to cPanel is the **Stage 22 index**. The older `assets/index.html` in the archived host backup is NOT the live baseline.
- Nested `file manager host.zip` contains `public html.zip`, then `assets.zip` (78 paths), `online.zip` (45 paths), `world.zip` and other archived components. These are backup inventory, not proof of the current Document Root contents.
- In archived `online.zip`, retain existing engines: `station_isohyet_v26.html`, `meteo_toolbox_v22.html`, `forecast_verification_v22.html`, `bulletin_maps_v21.html`.
- In archived `assets.zip`, `metstat_geo_r203.js` already implements a **five-level geographic selector** and county lookup against existing `CQC_LAYERS`. Do not build a second competing geographic picker. Its existing choice of unavailable scope is intentionally fail-closed.
- Existing archive contains `assets/map_layers.js` and atlas station/border resources. Preserve and verify hashes/dependencies before replacing anything.

## Targeted remaining integration
1. **R5 index compatibility:** rebase any Stage 27 overlay onto the *exact* Stage 22 deployed index + Stage 26 verified loader. Hash-check that base first. An archive-level index is not a substitute.
2. **Geographic region zoom:** test the existing `metstat_geo_r203.js` selection handler against actual `nvReg` engine behavior, province/county geometries and published tile coverage. Do not claim a county weather raster merely because borders/zoom exist.
3. **FA/EN parity:** geographic dropdowns, buttons, status messages, errors and all restored modules must use live language state. No Persian static UI words in EN mode; preserve scientific parameter IDs, coordinates and data values.
4. **Security:** no automatic execution of archived installer/repair PHP endpoints, no unverified script replacement, no unsafe dynamic HTML; inspect PHP error display/access controls and test module sandbox/policy for compatibility. Report, do not delete, any divergent files until backed up.
5. **R5 layout:** desktop-like grid on all devices as authorized. Existing colored model buttons move to the horizontal top row in fullscreen; do not add duplicate button sets. Check collision, scrolling and minimum tap size in both languages.
6. **Verification:** route/404 checks on the live canonical forecast route, module smoke tests with valid sample data, time/locale toggling, same-cycle data provenance, page load performance and rollback to Stage 22. No production merge until green.

## Parallel NWP implementation work
- ECMWF is one logical model. For each parameter × pressure level × run × valid hour × area, priority `ecmwf_ifs` (~9 km) then `ecmwf_ifs025` (~28 km) **only for verified same-run fields**. Example +0…+240 from high-res if available, +246…+360 from low-res only when it actually exists. The 00/12 360-hour horizon does not imply the same horizon for 06/18 cycles.
- GFS is one logical model, priority `ncep_gfs013` (~13 km), fallback `ncep_gfs025` (~28 km) per variable/hour. One frame, one provenance record, one physical-model vote.
- Existing `nwp_unified_resolution.py` and `global_nwp_stage.py` already implement portions of this policy. Extend them rather than add another independent resolver. However, current `nwp_maps.py` still exposes separate legacy `ecmwf9` / `gfs25` production IDs. Avoid breaking bookmarks and existing assets.
- AI: independent `aifs` = ECMWF AIFS Single and `aigfs` = NOAA AIGFS. Stage 1 geography is Middle East + Turkey, and only total precipitation and Z500 until real GRIB fields are QC-validated. No AI field can be added to the 60%/40% physical multi-model as a hidden sixth vote.
- PR [NWP #32](https://github.com/monsoonrain83-hub/metstat-nwp/pull/32) adds independent AI source-preflight code and resolution-policy tests; it does NOT publish charts or modify cPanel.

## Explicitly NOT completed
Full AI GRIB decoding/regridding, scheduled download, published maps, host Stage 27 overlay, all-language UI verification, actual combined ECMWF/GFS production and live-site verification. Each needs separate test evidence and approval before production deployment.
