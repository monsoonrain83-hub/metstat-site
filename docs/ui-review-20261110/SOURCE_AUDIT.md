# MetStat UI — source audit and deployment gate (2026-11-10)

## Verified from reconstructed r193 source
- `src/js/34_online.js` builds the online page dynamically. `onBuildUI` injects `nvViewerHTML()` only when a nonempty manifest is available; it then initializes `nvInit()` and calls `nvrBuild()`.
- `src/js/82_nv_rows.js` reorders live DOM controls into map, legend, model chips, forecast time, advanced dropdowns, and mirrored model/parameter selects. The legacy controls are deliberately retained and mirrored through `wxSet`.
- `nvrBuild` uses `data-rows` to avoid repeated row construction; its synchronization loop refreshes every 700ms.
- `nvMenus` moves into `onAside` at viewport widths >=1000px and moves back below that threshold; the move is also conditional on `nvfOn`. Any responsive redesign must respect this logic rather than duplicate controls.
- The P1 CSS is limited to the model-chip row, forecast-time control sizing, focus styles and reduced-motion support. It is **not** a full responsive redesign.

## Three distinct viewport test targets
1. Mobile normal: 390×844 CSS pixels (touch).
2. Mobile browser Desktop Site: approximately 980×844 *layout* CSS pixels with a small physical screen. This must be checked on actual Brave Android because viewport emulation is not identical.
3. Desktop PC: 1440×900 CSS pixels (mouse/keyboard).

## Attempted browser test
Playwright and Chromium were present, but the execution environment blocked navigation both to `file://` and a local `http://127.0.0.1` server with `net::ERR_BLOCKED_BY_ADMINISTRATOR`. Therefore **no successful rendered-browser screenshot or interaction test** was performed. Do not describe this as passed.

## GitHub deployment risk
The default-branch workflow `.github/workflows/deploy-site.yml` watches `site_src.zip`, `site_src.part*`, `site_patch*.zip`, and `nwp_upload.php`, then builds, runs Playwright smoke tests and FTPS-uploads `dist/`. Thus any production-path change on main could trigger an immediate host update.
The current site source is stored as a binary `site_src.zip`; the GitHub connector did not expose its bytes as usable UTF-8. Therefore source parity with the reconstructed r193 archive is **not established**.

## Next safe engineering gates
1. Obtain and unpack the exact current `site_src.zip` (or source archive), and compare to the r193 reconstruction.
2. Apply the P1 patch to that exact source, not to an assumed identical copy.
3. Verify CSS selectors and check all online-map interactions (model, run, variable, valid time, overlays, GIF, saved image).
4. Run screenshots + keyboard/touch regression in three viewport modes.
5. Build a full deployment archive and use a staging FTPS destination or explicit release gate; do not merge a deployment-triggering file on main until verified.

## Status
GitHub review branch + draft PR exist. No production changes, no host-ready artifact yet.
