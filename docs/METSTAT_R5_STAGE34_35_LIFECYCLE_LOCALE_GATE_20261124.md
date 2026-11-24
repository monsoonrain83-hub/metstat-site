# MetStat R5 Stage34–35 — exact uploaded host source, viewer lifecycle + bilingual native geographic controls

**Date:** 2026-11-24. **Status:** reversible staging candidate only. No cPanel deployment or real NWP publication verified.

## Source and target SHA-256 (exact bytes)
| Variant | Active `index.html` SHA-256 | Overlay for Stage35 |
|---|---|---|
| Original uploaded host 2026-11-24 04:18 | `a6d3c06bb3197671e2a7e1f3e2043b924a23ee35c76ca4f35ef9d1e1c66a90d8` | 4 files: index.html, original R201 CSS+JS replacements, stage24 restore JS |
| Stage32 | `b3d7121fbdf99cfc838dc567bf4fc163bf64809d359031e5d2c06052ff0f432a` | index.html only |
| Stage33 | `4e4e0990df3d0f2a8bd4e503efdb7751cb724dd3e6e7f47e64b749d8eba5ce6b` | index.html only |
| Stage34 | `65fbed2f1ff1af457d3a24a37fe8f701cff6576edbd70176847cff9794c6bb8e` | index.html only |
| Other | — | **Fail closed: do not install; fetch latest actual cPanel bytes** |

**Target index SHA-256:** `e2d95e51561b64fbaa449891c3957c337880353b027fd4581e5013810e8b0f9b`.

## Stage34: functional performance repair in actual host HTML
- Original `nvInit()` created a new `ResizeObserver` on each viewer rebuild without disconnecting the previous observer. Stage34 stores the observer in existing `NV` state and disconnects before a replacement.
- Native `nvFillModels()` now emits `metstat:nv-model-options` after the actual model options are populated.
- R7 `badgeModel()` is called by the actual native model-change event / emitted ready event; fixed `setInterval(badgeModel,1800)` was removed. The same original model selector/badge remains, without a duplicated control.
- Test executed actual `nvViewerHTML()` and `nvInit()` twice in a browser with a counting `ResizeObserver`: **Stage33 created=2, disconnected=0; Stage34 created=2, disconnected=1; Stage35 same result**. Exactly one original model badge, no JS page errors.

## Stage35: FA/EN five geographic selectors in actual R7 owner
- The original `syncGeo()` produces FA/EN area title, five selector labels/ARIA labels and common option names, re-synchronized via existing `langchange` (no polling).
- Preserves the **same five native select elements**, unchanged keys, option values, selected geography and disabled county control; cannot fabricate unsupported country/province geometry or world coverage. Province names from the Persian source geo dataset remain Persian.
- Actual `#langBtn` click exercised FA→EN and converted the Iran option to **Iran** in Chromium without page error.

## Offline validation
- 14 nonempty inline JS scripts syntactically valid, 19 script tags total; only script blocks 11 and 14 differ from Stage33, with exact source/target SHA.
- All inline CSS unchanged compared with Stage33, **1,138 `!important`** remain (zero added), 271 unique HTML IDs, no new GIS or image/embedded font changes.
- Chromium at 1440×900, 960×720, 844×390 and 390×844: seven nav groups same row, sidebar width 328px (desktop CSS layout), five geo selectors, English & Persian switch, repeat viewer mounting and no pageerror.
- ZIP CRC and file SHA, six overlay/rollback packages and Persian cPanel guide were prepared locally and delivered in this chat. **Host binary ZIP bytes were not committed to GitHub**; do not attempt to reconstruct ZIP from this Markdown.
- No claim that PHP, live NWP manifest, real model fields, exact extent/time, commercial web auth, PNG/GIF export, full R5 visual parity, mobile physical touch, or seasonal automation has been tested. Administrator must verify on isolated staging, then approve any live deployment.

## Next required engineering gates
1. Audit `nvInit` on all code paths including exit and animation playback timer cleanup; avoid impacting actual forecast GIF/playback.
2. Improve global geographic selection only when **real bbox/tiles** exist and safe per-item model fallback is implemented; don't represent Middle East map as full Asia/world.
3. Compare reference R5 against production on **valid live model** (not synthetic no-data screen); follow screenshot acceptance + 404 route + API + model/GIS provenance + isohyet/verification/toolbox regression.

Reference: `METSTAT_MASTER_REQUIREMENTS_1405-08-30_v1.md` and `docs/METSTAT_R5_UNIFIED_ROADMAP_20261123.md`.
