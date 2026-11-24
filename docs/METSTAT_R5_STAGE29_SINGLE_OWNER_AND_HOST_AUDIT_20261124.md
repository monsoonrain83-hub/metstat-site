# Stage29 R5 + host: remove competing fullscreen relocation owner
**2026-11-24, staging only.** Active `index.html` on cPanel is Stage22 per administrator; do NOT deploy this Stage29 delta over Stage22 without a proven Stage28 base.

## Verified Stage29 difference against Stage28
- Input staged ZIP: `MetStat_R5_STAGE28_CONSOLIDATED_DEPENDENCIES_STAGING.zip`; input `index.html` SHA256 `a7646948ebd22e0b7d5b794ff6ff419a9d79873e085145322888b9b8e4be0f83`.
- New `index.html` SHA256 `52c472adc7e2ff6f4b4ffb413595c914895d422cb8d8ab69a8349a8a3bd029eb`; full Stage29 ZIP SHA256 `2a4471c3482e6591ce4c9c4edbbf9f039450191b7a63c046aca9da53747f24c3`.
- Remove redundant R205 `metstat_original_model_chips_horizontal.js/.css` file and its 2 HTML references; the existing native R7 `nativeFullscreenDock()` / `restoreFullscreenDock()` remains the sole fullscreen model-chip owner and moves the **original `#fsMods` node**, never copies buttons. Existing opt-in R6 canary logic is not auto-enabled or removed.
- In existing `assets/metstat_r5_stage24_restore.js` only, localize known status and error text plus `iframe.title` for FA/EN and react on `langchange`. **No general translation of the four legacy HTML engines is claimed**.
- Staged file count 17→15; 13 files unchanged; only `index.html` and `assets/metstat_r5_stage24_restore.js` change. Four original engine HTMLs, GIS boundaries, station atlas, all NWP outputs and Base64 remain identical.
- All nine local script/style references resolve within staged ZIP, Node syntax for all 14 inline scripts and all standalone JS passed.
- Chromium fixture using **the actual inline R7 script extracted from the site's index**: 4 viewports (390x844,844x390,960x720,1440x900) × FA/EN, enter→exit twice each: 8/8; bilingual iframe status/title cases: 2/2. No page errors in those fixtures. Not a real deployed app E2E test.

## Host archive / quarantine inventory
The previous host archive (nested `file manager host.zip`) contains old browser installer, repair and rollback PHP scripts. A **read-only** 266-path virtual snapshot scan found 7 candidate installer/repair URLs. Only two have filename references in other static files, but static non-reference cannot prove runtime nonuse. Candidate SHA files are in the delivered `METSTAT_STAGE29_HOST_QUARANTINE_AUDIT.json`; no live deletes or access-control modifications were made. Back up and inspect live access logs/route reachability before denying access or moving any file outside public_html. PHP lint and keyword grep are NOT malware clearance.

## Parallel NWP
NWP PR [#34](https://github.com/monsoonrain83-hub/metstat-nwp/pull/34) acquired live 16x16 OM meteorological samples in the source run:
- AIGFS +6h: temperature ~26.95°C, Z500 ~5900m valid; precipitation missing in sampled OM file => **not QC passed**.
- CMA GRAPES +6h: temperature ~27.4°C, Z500 ~5901m, precipitation raw ~0.9 => sample QC passes.
- JMA GSM +6h: temperature ~27.3°C, Z500 ~602 dam, precipitation raw ~1.3 => sample QC passes.
- None are production-ready: accumulation semantics, full-domain/coordinate orientation and official-source priority still need validation. Other source candidates and native 9km/13km fallback remain separate requirements. See GitHub Actions read-only model-field-qc artifact.

**No merge or cPanel deployment authorized by these QA results.**
