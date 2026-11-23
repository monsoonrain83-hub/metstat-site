# MetStat Stage28 — canonical R201 controls and host-asset reconciliation
Date: 2026-11-24 (Asia/Tehran). **Staging only; not live deployment.**

## Inputs and provenance
- User confirmed live cPanel root `index.html` is Stage22; old archived `assets/index.html` is not an acceptable replacement.
- Local base: `MetStat_R5_STAGE26_FULL_STAGING.zip`, index SHA256 `a6d3c06bb3197671e2a7e1f3e2043b924a23ee35c76ca4f35ef9d1e1c66a90d8`.
- Archive: user-supplied `file manager host.zip` → `public html.zip` → `assets.zip`.
- Real output: `MetStat_R5_STAGE28_CONSOLIDATED_DEPENDENCIES_STAGING.zip`, SHA256 `61362afaf083579dfd365fe96cf39005db2c766a4313f92d3ad16e1ddbb39835`.
- Result `index.html` SHA256 `a7646948ebd22e0b7d5b794ff6ff419a9d79873e085145322888b9b8e4be0f83`.
- Full source and offline tests delivered with user-facing ZIP and `METSTAT_STAGE28_QA.json`.

## Actual source cleanup
Prior Stage26 ZIP had 16 files and exactly **3 referenced but absent assets**:
`assets/metstat_original_model_chips_horizontal.css`,
`assets/metstat_original_model_chips_horizontal.js`, and
`assets/metstat_map_ui_r201.css`.
The archived assets' checksums are:
- chips JS `65337607a11474c7afc729a0ce4c9100945b8005a63d29785e120f93101677fe`
- chips CSS `a0e6225ef3251cfab60d0d84650d70531e3961ac3dab4925cadfcb3e1783cc77`
- R201 CSS `129c08eea0ec16dda407b5f2124ff325787a0b49eaffe7a7afc7e545b8f23940`.

Stage28 reuses those exact archived bytes and **eliminates the two separately referenced Stage19 map-control files**, folding their behavior and styles into the one real R201 asset owner:
- `assets/metstat_r5_stage19_controls.js` removed from staged ZIP and `index.html`
- `assets/metstat_r5_stage19_controls.css` removed from staged ZIP and `index.html`
- R201 JS now contains the existing R201 behavior *then* existing Stage19 IIFE, without another control or event subsystem.
- R201 CSS contains the original Stage19 map-specific rules and existing archived R201 CSS.
- Restore loader, archived engines, GIS boundaries, station atlas, model data and inline Base64 are unchanged.

Staged file count 16 → 17 (2 removed, 3 restored). All 11 local JS/CSS references are present in output. **No new timer, MutationObserver, endpoint or model state** was added.

## QA and deployment gate
48 offline assertions successful: exact source-prefix and adapter code, no duplicate DOM IDs, all referenced local assets in archive, 4 viewport sizes × FA/EN toggles for merged R201+Stage19 map-control harness, Node.js syntax for external and inline scripts, unchanged archived engines/atlas/map layers, valid ZIP CRC. This does not establish authenticated PHP/runtime rendering or true scientific output. `tools/r5_stage28_bundle.py` reproduces staging from the user-provided two source ZIP files (install `beautifulsoup4`).

**Do not deploy this entire ZIP blindly.** Check current LIVE cPanel SHA and all same-name assets, backup outside the web root, validate staging routes and data. Do not delete archived live files unless dependency-search, rollback inventory, and controller ownership tests establish they are unreferenced.

## Parallel NWP work
- `metstat-nwp` PR [#34](https://github.com/monsoonrain83-hub/metstat-nwp/pull/34) adds a read-only seven-model S3 inventory probe, plus actual GitHub Actions JSON artifact.
- Probed successfully: `ncep_aigfs025` (87 vars), `cma_grapes_global` (258 vars), `jma_gsm` (78 vars).
- Unreadable tested paths: `ecmwf_aifs025`, `gfs_graphcast025`, `ncep_gfs_graphcast025`, `kma_gdps`, `google_weathernext2_ensemble`; AIFS and GraphCast are not proven unavailable on their originating centers or all possible datasets.
- KMA GDPS is marked **discontinued in Open-Meteo as of 2026-03-31**, do not present as live until a new official source is proven.
- Probe found no `nx/ny` or other grid geometry keys in the observed `latest.json`; grid must be independently validated from OM file metadata/official domain definitions, never guessed.
- Existing per-variable ECMWF9→28 and GFS13→28 priority remains the authoritative policy. NWP PRs #32 (AI staging), #33 (60/40 +180h), #34 (read-only source probe) are isolated from the R5 site ZIP.

## Next atomic work
1. Confirm Stage28 cleanup on actual Stage22 host staging with R201 asset owners; remove abandoned duplicated controllers only after dependency graph confirms no reachable route.
2. All-pages R5 right-sidebar 328px and left-map + bilingual FA/EN controls, full/portrait/landscape tests, no parallel geographic selectors.
3. NWP source-level field/lead/geometry QC for proven AIGFS/CMA/JMA, fallback from official centers first; then optional modules and global product regridding.
4. Full live NWP chain/manifest/stale tracking and secure cPanel rollback.
