# MetStat R5: Stage23 — restore existing host engines, do not rewrite
Date: 2026-11-23 | Status: archive reconciliation + **staging candidate only**, NOT live deployment.

Input: user-provided `file manager host.zip`, nested `public html.zip`. The archive contains the original `online/station_isohyet_v26.html`, `online/meteo_toolbox_v22.html`, `online/forecast_verification_v22.html` and `online/bulletin_maps_v21.html`. The new Stage23 candidate reconnects these four engine pages to the existing seven-group R5 navigation; all legacy module bytes and scientific processing are untouched. Old Stage22 converters are preserved (overlap must be resolved before removing an implementation).

## Source identity and release
- Stage22 base `index.html` SHA-256: `339f863f863aef5a33e5567c5ec03d06a57fe9da8ad3ba908e62d2e4e73c44cb`
- Stage23 candidate `index.html` SHA-256: `a04449545d33e303453f5ea63e0d52303911332924f1f084e02e1f6af8472aef`
- Staged user-delivered ZIP: `MetStat_R5_STAGE23_EXISTING_MODULES_RECOVERED_TEST.zip`, SHA-256 `14320d400b2783d73c10d2dffc81a56465208f2068f8ecc466492cf033a1b975`.
- The bundle contains the complete Stage22 index and unchanged assets, four archived engine pages, `assets/map_layers.js`, `online/atlas_stations_v28.json`, and **two new** archive-loader JS/CSS files. It excludes admin/private material, installers, PHP configuration and logs.
- The new archive loader fetches only four hard-coded, same-origin HTML paths and verifies SHA-256 before framing, refusing missing/mismatched versions. This is not a complete security sandbox.
- A native page title bug is repaired: route breadcrumb updates no longer overwrite the "full view" button text.

## Critical findings
1. The supplied archive **does not contain root `index.html`**. Its `assets/index.html` is an older candidate, SHA-256 `52e16fb3afbcd5e6e571fa8a42e939d03e3274a1925cdc48a47085e3f17de881`. It is NOT proof of the active cPanel document root.
2. Its `version.json` advertises UI r122 although R201 and Stage20–22 files coexist. Both R201 asset hashes differ from `RELEASE_MANIFEST.json` values. Suspect version drift, not confirmed malware.
3. Public-file snapshot includes obsolete browser installers/rollback PHP, error logs, and PHP config with `display_errors=On`, and references PHP 7.4. Confirm actual server policy; restrict old web installers only after recovery and external backup.
4. `meteo_toolbox_v22.html` already implements meteorological calculations, IDW and basic GIS/format conversion. New Stage22 text/CSV/GeoJSON conversion overlaps it. No deletion yet: establish canonical route/engine after safety/quality review.
5. `world.zip` is not proof of live global coverage. Some names embed a future cycle `2026120712` relative to audit date, and samples are limited to WebP fields.

## Tests and limits
- 30 JS syntax checks passed; 59 PHP files passed local syntax lint; embedded 20 Base64 payloads and every Stage22-shared asset remained byte-identical.
- 16/16 Chromium **offline navigation/fail-closed** tests passed across portrait/landscape phone and two desktop sizes; four original engine DOM templates parsed. The toolbox's RH calculation and CSV-to-JSON download were exercised.
- Chromium URL navigation was blocked in the testing environment. Accordingly real same-origin iframe mounting, remote live API data, authentic GIS matching, complete rain isohyets, and host PHP execution are NOT certified.

## Roadmap integration (P0–P7 still active)
P0 first authenticate ACTIVE cPanel file hashes, dependency graph and secure recovery; P1/P3 finalize recovered real module paths and R5 two-column UI; P2 complete English/Persian; P4 unified ECMWF 9/28 and GFS 13/28 plus AIFS/AIGFS/world; P5 anomaly/week/SEAS and publication QA; P6 GIS county/stations/rain XLSX/floods; P7 security/performance controlled release.

**No automatic deploy.** Stage with its own Document Root, test with real data, secure uploader/install scripts, obtain admin approval, then merge/restore with rollback. Full Persian report + updated roadmap are preserved in the conversation artifacts.