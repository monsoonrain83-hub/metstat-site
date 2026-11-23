# R5 Stage20 — six real-module workspace geometry check (no deployment)
Date: 2026-11-23. Reference: OPEN_METSTAT_R5_ANDROID_FIXED(1).html; master roadmap docs/METSTAT_R5_UNIFIED_ROADMAP_20261123.md.

The Stage19 `index.html` binary SHA256 is `d06bcb5b8504385f35334c21a1f120aa7d7ee72568476f026194d4814869f7f0`. The tested Stage20 HTML SHA256 is `5aba01fa0cbc9b6f1c3ee4908cf8923587d0173df160cb47250f47006ced1ee8`.

One new CSS link is added to the *existing* Stage19 HTML, without editing any inline JS, Base64, model formulas, GIS source or older assets:
```html
<link rel="stylesheet" href="assets/metstat_r5_stage20_workspaces.css?v=20" data-ms-stage20="1">
```
Stage20 CSS SHA256: `366286ef9af67f91c1103630e6eaeb4482d9d551d8095d285d0c11bc8db83b39`. The reviewed complete staged files are in the matching user-delivered ZIP `MetStat_R5_STAGE20_SIX_WORKSPACES_TEST.zip`. This PR tracks QA/provenance ONLY, not the deployable binary.

## Actual staged changes
Use the same desktop two-column geometry (328px logical right controls, remaining left map/chart) for existing DOM structures: ciMain/cxSel & ciSel climate indices, saMain satellite, sfMain monthly-seasonal, mtMain mountain, synApp gridded synergy, flMain flood layout. Preserve each module's actual functions, API calls, map canvas and bindings; don't clone or move them. Keep satellite's saWide exception.

## Measured QA
Four Chromium viewport sizes 390x844, 844x390, 960x720 and 1440x900, both fa and en, six module DOM patterns: **48/48 geometry assertions passed**. Climate, satellite, mountain, seasonal and synergy use the actual HTML-producing code. Flood uses a skeletal structure from the existing template because actual basin data were not available; **live flood functionality is NOT tested**. All inline JavaScript scripts pass node --check and all embedded Base64 payloads match exactly.

## Outstanding, not claimed as complete
Complete live model/data/PNG-GIF QA; cross-page translation of all dynamic labels; real Iran county geometry and global extents; 9/28 ECMWF + 13/28 GFS fallback and AIFS/AIGFS actual producer/manifest integration; weekly, monthly and seasonal publication; site/server PHP upload and authentication/security audit. No changes to cPanel or main-site release were made.

**Controlled release requirement:** compare active cPanel file SHA and assets first, back up outside public_html, validate on staging and obtain administrator approval. Do NOT merge assuming this doc updates deployed index.html.