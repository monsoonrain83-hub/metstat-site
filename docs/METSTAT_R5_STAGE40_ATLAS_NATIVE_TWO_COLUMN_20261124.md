# MetStat R5 Stage40 — climate atlas return to TWO columns, preserve both native settings groups

**2026-11-24 — QA-only release candidate; no cPanel deployment, no PR merge.**

## Failure reproduced from Stage39 candidate

The user explicitly required the previously correct R5 two-column design for the climate atlas. Source inspection of the exact 6.5 MB host index established that the real native Atlas creates **two sidebars**: initial `#caAside` and dynamically inserted `#caAside2` by `caLayoutSplit()`, plus `<main>` containing the existing atlas map/chart cards.

Stage39 had assigned `grid-column:1;grid-row:1` to **every** `#caApp>aside`. An actual Chromium fixture with native `caLayoutSplit()` yielded **two distinct sidebars at exactly the same x/y coordinate**, hiding one group beneath the other at 1440px. At 960px and below, older `.wrap` mobile CSS changed the Atlas from grid into a stacked flex column; `caCollapse()` and `caMobileReveal()` then automatically hid or collapsed the original settings.

The initial Stage39 "12 routes x 4 viewports no pageerror" checks did not create `#caAside2`, and therefore were **insufficient acceptance coverage**. The Stage40 browser QA repairs that gap explicitly.

## Source pin and bounded fix

- Stage39 source index SHA256 `9dc68b50c2e8817e8e1b9996d8fd7d48f6defd016aca0a8cdd9a10c949d93e0e`.
- Stage40 target index SHA256 `3b80f0e8db2334e1e0a0febe3acd17f84ba89dcac09b2f1632353f61d8859958`.
- The exact original R5 visual reference remains `OPEN_METSTAT_R5_ANDROID_FIXED(1).html` SHA256 `2792e674660f07135acb91f6cbf92f8740f4c9ff8c073e94767927b1c8dbadf9`.
- In the existing **single** `ms9-desktop-r5-system` CSS owner, `#caApp` always uses a 2-track RTL grid: right variable 328px desktop / 230px landscape, left remaining width. The original first aside sits row 1 of the right track, the dynamically created second aside row 2 of that **same** right track, and the original main fills the left track across both rows. No cloning or moving original controls.
- Original mobile stacking and toggle are disabled **only when `html.ms9-active`**, not for external legacy pages. Exactly two native JS guards are added to `caCollapse` and `caMobileReveal`; no new observer, timer or event listener.
- Existing no-data Atlas explanatory panel displays when `#caEmpty` is not marked hidden, including landscape mobile.
- All scientific calculations, input data, station matching, chart/GeoTIFF and image creation, backend NWP, GIS, PHP, and site routes are **untouched**. Only original JS script block 11 and CSS style block 5 differ. The number of `!important` entries stays 1,138.

## Evidence: two real native groups, not an empty Atlas fixture

Using isolated Chromium and executing **the actual `caLayoutSplit()` function** after injecting harmless layout-only sample controls (not fake scientific values), we tested these viewports: 1440×900, 960×720, 844×390, 390×844. For each, 12 explicit assertions verify: exactly 2 grid tracks; both groups same right track at nonoverlapping y offsets; main left with 4px+ gap; original 5 grouped panels and IDs retained; no automatic collapse; no extra geo controls; seven header groups; no unexpected page overflow (390 uses intentional 960px desktop panning); no pageerrors. All **48/48 assertions** passed. Screenshots from before and after are in the QA-only ZIP.

A separate **48-case real route smoke** for 12 modules × 4 viewports found 0 JavaScript errors. **All 44 non-Atlas route/view pairs had identical computed element positions, grid values and visibility** versus Stage39. The full existing 19-script index has 15 nonempty JS script sections checked with Node; all pass syntax check.

This checks frontend layout behavior **without** asserting actual climate station DB response, live generated map/chart PNG/GIF, real 404-free host routes, physical Android swipe, security or Figma parity.

## Installation / rollback

Three **mutually exclusive, hash-matched** upload paths delivered to the administrator in chat:
- Original user-supplied host index SHA `a6d3c06bb3197671e2a7e1f3e2043b924a23ee35c76ca4f35ef9d1e1c66a90d8` **plus exact matching original assets** → 4-file Stage40 ZIP.
- Exact Stage37 index SHA `a6ee0843b29c300ec083ef0d7c636eb759ee4dd3eb9ea90d38079d5240243aa1` + matching assets → Stage40 index-only ZIP.
- Exact Stage39 index SHA above + matching assets → Stage40 index-only ZIP.

Source-specific rollback ZIPs are separate. For Stage32–36 or **any newer host automation SHA**, refuse overwrite and rebuild against the current active bytes. All archives verified for path, member count, SHA256 and CRC. User install guide and QA-only source files are in the ChatGPT-delivered artifacts; never upload QA ZIP to cPanel.

## Next acceptance gate

Get exact live cPanel file hashes, backup outside webroot, stage the correct package, run real station DB and outputs on Atlas, both languages, all four viewport modes, original control interactions, PDF/PNG outputs, 404/API smoke on NWP, isohyet, toolbox and verification. Only then administrator-approved deployment. **Stage39 is superseded for Atlas because of the observed sidebar overlap.**

Figma file read/sync remains blocked by missing Editor permission; GitHub UI UX Pro Max checklist is subordinate to the user’s R5 design.
