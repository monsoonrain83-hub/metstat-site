# MetStat R5 Stage32 — host-source candidate, 2026-11-24

**Status:** packaged for **administrator-reviewed staging**, not installed, not a complete R5 migration.

## Exact source
User-supplied active-host candidate `index(20261124-041820).html`: `a6d3c06bb3197671e2a7e1f3e2043b924a23ee35c76ca4f35ef9d1e1c66a90d8` (6,482,823 bytes). Submitted `assets.zip`: 80 assets and one directory, ZIP CRC valid. This is the Stage26-index SHA; **it is not the former Stage22 SHA**.

An older `assets/index.html` also exists in the archive; never treat it as the live canonical document.

## Produced outside GitHub
Two **exact four-file** ZIPs were delivered in the current ChatGPT conversation: candidate overlay and exact-byte rollback. The archive bytes are **not GitHub code changes**. No secrets, huge host HTML, or uploaded assets were committed to this PR.

1. `index.html`: remove four redundant Stage19/R205 script/link tags; refresh versioned canonical R201 references; use Persian as first-visit fallback for `mmap.lang` while preserving saved preferences.
2. `assets/metstat_map_ui_r201.js`: concatenate original R201 with already-existing Stage19 IIFE, eliminating separate script load without cloning NWP fields/controls.
3. `assets/metstat_map_ui_r201.css`: consolidate existing Stage19 CSS with exact original R201 CSS.
4. `assets/metstat_r5_stage24_restore.js`: existing archived-module integrity messages, title and language-change sync get explicit FA/EN; **legacy iframe HTML remains untranslated**.

The original R7 `nativeFullscreenDock()` / `restoreFullscreenDock()` retains sole ownership of the **same original** `#fsMods` node. No new data pipeline, scientific engine, model source or geographic coverage was added.

## Offline evidence
- Target index SHA-256: `b3d7121fbdf99cfc838dc567bf4fc163bf64809d359031e5d2c06052ff0f432a`.
- 271 HTML DOM IDs, none duplicated. All referenced local JS/CSS resolve against supplied `assets.zip`.
- Existing inline CSS `!important`: **1138 → 1138**. Original inline images/fonts exactly preserved, protected `map_layers.js`, `terrain_dem.js`, `atlas_pack.js`, `data_borders.js`, `data_terrain_b64.js`, `tt_me_overlay.js` unchanged.
- 14 inline JS + 2 modified standalone JS passed Node syntax checks.
- Browser smoke at 390×844, 844×390, 960×720, 1440×900: R7 shell, five geographic selectors, no JavaScript page errors.
- Native fullscreen fixture: two enter/exit cycles, exactly one `#fsMods`; original parent restored on exit.
- Offline fixture did not contain `auth.php`, `data/geo_extra.json`, `online/ai_proxy.php`; no conclusion about live endpoints.
- No PHP, real NWP data, host `.htaccess`, station database, server-side authentication or full R5 pixel-parity test passed or was claimed.

## Publication gate (fail closed)
Never install this overlay if the **current** active `public_html/index.html` no longer hashes to `a6d3c06b...`; a scheduled automation or other upload could have changed it. Back up the exact four live files and the full host **outside** public_html, stage in an isolated document root, test live route 200, models, actual GIS boundaries, EN/FA, fullscreen, isohyet, toolbox, verification, bulletin, mobile, PNG/GIF and rollback. **Do not combine** prior Stage28/Stage29 ZIPs with Stage32.

This Stage32 package closes a subset of R5 P0/P1/P2 owner conflict and locale gates. It does **not** complete global models, anomaly production, GIS, real NWP maps or full R5 design.
