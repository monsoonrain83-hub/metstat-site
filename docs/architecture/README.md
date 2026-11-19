# MetStat architecture atlas — r109 (hybrid, not deployed)

> Snapshot: 2026-11-19. This documentation is **not a deployable patch**.
> Frontend facts come from the local r109 package layered on r108; backend import edges come from a separate Graphify snapshot.
> Live host code has **not** been verified to match these files.

## Coverage and limitations

| Codebase | Graphify | Evidence |
| --- | --- | --- |
| monsoonrain83-hub/metstat-maps | Indexed, 438 nodes / 816 edges | commit 00fa91b7c277bd866373cb7ce7a7f2f88bf825fc |
| monsoonrain83-hub/wtafkik | Indexed, 79 nodes / 160 edges | Android Kotlin MapOverlay app, **not** MetStat web frontend |
| monsoonrain83-hub/weather-model-ensemble | Indexed, 117 nodes | Separate Next.js project, not verified to be the deployed site |
| monsoonrain83-hub/metstat-site | Not enabled for Graphify agents | This repository holds site_src.zip and older patches |
| monsoonrain83-hub/metstat-nwp | Not enabled for Graphify agents | Operating NWP code, distinct from metstat-maps snapshot |

## Local frontend baseline

* 44 known routes across 6 principal navigation groups (see ROUTES.csv).
* Shell: index.html, assets/metstat_core_v105.js, .htaccess, sitemap.xml
* Weather model UI: assets/metstat_core_v105.js, assets/map_layers.js, data_borders.js
* GIS/population labels: assets/map_layers.js, assets/metstat_osm_settlements_v98.js
* Station interpolation: online/station_isohyet_v26.html + atlas_station_registry_v33.js
* Embedded tools: online/meteo_toolbox_v22.html, online/forecast_verification_v22.html, online/station_isohyet_v26.html
* RTL/LTR: metstat_r96_desktop_shell.css, metstat_r97_layout.css, metstat_r102_english_layout.css, metstat_r109_targeted.css
* Admin: admin/index.php, admin/ui_audit.php, admin/site-health.html
* Analytics: metstat_tracking_config.js, metstat_ga4_v105.js

File hashes used for **local** r109 inventory:
* index.html SHA256: 6b6067b831a8fa91 (prefix)
* Verify exact deployment using full SHA256 from the generated archive before making changes.

## Verified import relationships from Graphify

* nwp_maps.py imports secondary.py, styles.py and warn_icons.py
* nwp_grid.py, ens_maps.py, lr_maps.py, ec46_maps.py import nwp_maps.py
* ens_maps.py and lr_maps.py also import styles.py

These edges are verified only for the indexed metstat-maps commit. Do not claim they directly describe deployed metstat-nwp until commits are matched.

## Before editing — change impact checklist

| Area | Mandatory regression checks |
| --- | --- |
| Routes / deep links | Direct URL, reload, browser back/forward, Persian/English, canonical URLs, Apache rewrite and sitemap |
| Atlas / meteogram | 2-column atlas; FA menu at right; EN menu at left; desktop-width view on mobile; no horizontal scrolling in subnav |
| Station matching | Fixed Chaharmahal/Bakhtiari sample; province checks; reject false Shahrestan / name collisions; compare fallback and authoritative atlas |
| GIS | Population-label collision, county boundary visibility, interaction latency |
| Model page | status colours/blinking, timesteps, map pan/zoom, spinner non-blocking |
| Independent tools | Full English translations of dynamic controls and iframe content |

## Deployment safety

The workflow `.github/workflows/deploy-site.yml` deploys to the live host on push changes to `site_src.zip`, `site_src.part*`, `site_patch*.zip` or `nwp_upload.php`. This documentation branch deliberately changes **none** of those files.

Do not merge updated site source to main until the actual host files, source hashes, and deployment workflow are reviewed.

## To complete full Graphify coverage

1. Enable **metstat-site** and **metstat-nwp** under repositories for the same active Graphify workspace.
2. Synchronize audited, non-secret, readable frontend source; do not merely upload a ZIP.
3. Re-index, then use graphify_file_neighbors / graphify_impact / graphify_trace against the specific indexed commit.
4. Compare new graph with the 44-route inventory and perform end-to-end tests before publishing.

_Maintained as source inventory and onboarding notes, not a substitute for production verification._
