# MetStat — Claude audits mapped to r109 and the safe r110 candidate

Snapshot date: 2026-11-19. This file summarizes audits from:
- `wtafkik_code_audit_and_prompt.md`
- `wtafkik_assets_audit_and_prompt.md`
- `wtafkik_url_seo_roadmap_and_prompt.md`

It is not a substitute for testing the **actual deployed cPanel files**.

| Area | Current source evidence | Decision / next verification |
| --- | --- | --- |
| 4.5 MB JS extracted from original HTML | Partly done r105, core still 4,505,948 bytes in r109 | Preserve initialization order; profile individual modules before split |
| Inline 316 KB upper-air lab | Present in r109 index; candidate r110 moves it byte-for-byte to a sync external script | JS syntax, function export, lab DOM smoke passed; full live browser test NOT passed |
| GA4 page views | Old r105 implementation includes hash/search and can emit duplicates | r110 candidate normalizes to canonical pathname and coalesces history events; mock tests passed; real GA4 ID not configured |
| 44 nested URLs | r108 manifest / .htaccess paths registered | Direct-URL/reload/Back/Forward tests on live host remain necessary |
| Sitemap metadata | 18 entries vs 44 manifest entries | Missing entries may be intentionally private; check indexability individually before addition |
| Fonts | 14 embedded base64 font faces in base_v105.css | Not removed: font files and licensing, FCP and visual baseline need validation; keep current CSS |
| CSS specificity | 22 inline style blocks in r109 HTML; many !important | No wholesale rewrite; create visual regression goldens before migration |
| 2.2 MB map_layers.js | Synchronous load in head | Identify first usage across routes and map functions before lazy-loading |
| Large weather.us overlay | r107 removes unconditional ~4.9 MB prefetch | Validate weather.us map, save and high-resolution export on live host |
| i18n EN | Independent iframe tools and generated JS still mixed-language in submitted screenshots | Extract source strings per page, test DOM and select options after each interaction |
| Station matching | r109 waits longer for atlas; sample 30 stations showed false matches historically | Fixed 30-row QC fixture; compare official station coordinates; never auto-place ambiguous sites |
| Admin health | Detail probe and dashboard implemented in earlier releases | Consolidate UI entry points only after admin/index.php source & auth audit |
| Security | innerHTML/document.write and GPX inputs need contextual inspection | Do not claim vulnerability from static counts; test untrusted sources; CSP Report-Only first |
| Accessibility / responsive | Desktop view on phone is a deliberate product requirement | Don't change width=1240 viewport without product approval |
| Production parity | GitHub Action deploys when site_src.zip / site_patch*.zip changes | Never merge a patch before comparing actual live host hashes to sources |

## Verified r110 candidate tests

- New upper-air script is identical to the former inline block (315,785 bytes) and evaluated without JS errors.
- `MET.C.Rd` and `window.labInit` exported; lab UI rendered 208 DOM elements in an isolated browser with no JS exception.
- Original index can be reconstructed **byte-for-byte** from r110 candidate after restoring script tag and GA4 cache-version reference.
- GA4 unit tests passed for one page view per canonical path, history events, hash de-duplication, excluding search/query details, invalid ID, and duplicate install.
- ZIP and `node --check` passed.
- **Live/browser navigation blocked in the execution environment**; no Lighthouse before/after or end-to-end production claim.

## Remaining staged plan

1. Verify current cPanel `index.html`, `.htaccess`, `assets`, `online/` and admin sources against r109 SHA; set a rollback snapshot.
2. Install tested changed-only r110 candidate after backing up and confirming correct baseline.
3. On the live host: smoke-test two languages, routes, model status colours and map refresh, atlas two-column controls, meteogram panel side, and upper-air lab.
4. Run Lighthouse under comparable conditions (mobile + desktop) and log LCP/FCP/TBT/CLS, transfer sizes and failed requests.
5. Only then profile and split GIS / CSS and address translation, stations and security in isolated pull requests.
6. Add Graphify agent indexing for `metstat-site` and `metstat-nwp` through the repository enablement UI; current Graphify connection cannot enable new repositories programmatically.

## Graphify coverage (do not conflate repositories)

`metstat-maps` indexed code is the map-production pipeline. `wtafkik` indexed project is Android Kotlin MapOverlay. `weather-model-ensemble` is a separate Next.js project. None proves parity with the deployed website.

_This document lives in a Draft PR. It does not change deploy artifacts and cannot trigger the FTPS deploy workflow._
