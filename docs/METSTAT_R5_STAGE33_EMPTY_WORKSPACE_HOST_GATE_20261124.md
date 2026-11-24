# MetStat R5 Stage33 — authentic no-data map workspace and guarded host overlay

**2026-11-24. Staging candidate only; no cPanel deployment.**

## Exact baseline and dependency
The administrator supplied `index(20261124-041820).html` plus `assets.zip`; Stage32 was constructed from these. Stage33 is a **pure HTML/CSS change on the exact Stage32 index**, no JS, model or layer change.

| Active host index SHA256 | Approved matching ZIP (provided in ChatGPT) | Number of files |
| --- | --- | --- |
| `a6d3c06bb3197671e2a7e1f3e2043b924a23ee35c76ca4f35ef9d1e1c66a90d8` | `MetStat_R5_STAGE33_INSTALL_FROM_ORIGINAL_HOST_FILES.zip` | 4 (Stage32 assets + Stage33 index) |
| `b3d7121fbdf99cfc838dc567bf4fc163bf64809d359031e5d2c06052ff0f432a` | `MetStat_R5_STAGE33_INCREMENTAL_IF_STAGE32_INSTALLED.zip` | 1 (`index.html`) |
| Other | **Do not deploy; rebuild from currently active cPanel content** | — |

Result `index.html` SHA256: **`4e4e0990df3d0f2a8bd4e503efdb7751cb724dd3e6e7f47e64b749d8eba5ce6b`**.

## Scope of the actual change
- The existing `#onEmpty` temporary card is rendered as a full-height R5-style map workspace instead of a small plain message. No invented weather map, coordinates, data source, or valid time.
- Crucially the old app writes manifest-load errors to `#onEmpty.querySelector('div').textContent`; the Stage33 **first child remains the real status host**, with `role=status` and `aria-live=polite`. A DOM smoke initially exposed this behavior and the release was corrected before packaging.
- New presentation copy has both FA/EN DOM spans, switched by the existing `html.lang`, with no new listener, polling, timer or JS. Existing status/error text continues to pass through the app's built-in localization.
- Existing CSS `:has(#onViewer .nvCard)` hides the temporary workspace as soon as a valid viewer is mounted. Stage33 is scoped to `#onApp #onEmpty`; genuine canvas, fullscreen, colorbar, science engines, GIS and archived modules are byte-identical to Stage32.
- The patch replaces one exact `#onEmpty` HTML section and inserts **one scoped CSS section** in the existing `ms9-desktop-r5-system` owner. No added `!important`, MutationObserver, setInterval, duplicate IDs or runtime controls.

## Tested evidence (not a production test)
- Four offline Chromium `set_content` viewports 1440×900, 960×720, 844×390 and 390×844, no `pageerror`, five real region selects, no repeated IDs.
- Confirmed original JS overwrites Stage33's status child without removing the workspace; confirmed in all four fixtures that the placeholder becomes `display:none` when the original `.nvCard` viewer is mounted. FA↔EN toggle and authentic offline warning translated.
- 14 existing inline JS syntactically checked with Node and **all 14 script bodies identical**; `!important` count 1,138→1,138; DOM IDs 271, no duplicates.
- SHA-pinned exact ZIPs + separate matching rollback packages, no PHP or live-file deletions.
- GitHub `tools/r5_stage33_release_gate.py` validates the pinned baseline, result, allowed overlay files, unchanged inline scripts for incremental upgrades, original asset SHA and ZIP integrity; accompanying tests exercise fail-closed behavior.

**Not verified:** actual cPanel route status, auth/PHP, model manifest, real field/extent, full Android gesture flow, actual PNG/GIF, isohyet, seasonal production or 1:1 R5 complete UI. Production still requires real staging deployment, no 404, NWP field checks and administrator approval.

## Next P1/P2 gate
Refactor R5 navigation/account/side control surfaces in original CSS/DOM owners rather than adding redundant overrides, with FA/EN × 4 viewport regression. Do not publish this no-data visual polish as a completed model or map product.
