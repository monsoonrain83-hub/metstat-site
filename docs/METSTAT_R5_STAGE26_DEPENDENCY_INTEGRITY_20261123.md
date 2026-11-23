# R5 Stage26: verified map dependencies (review only)
Date: 2026-11-23. Base: Stage25 full staged ZIP; active cPanel has not been independently audited.

## Fix
Only assets/metstat_r5_stage24_restore.js changes. HTML srcdoc was already SHA256-pinned; Stage26 adds browser-native SRI to its direct dependencies in the original station_isohyet_v26.html (without changing the original HTML file):
- assets/map_layers.js SHA256 b32b491c7105f77c7d23767dd8773f37edb9eda480b9067a2ace6f4d616380b8.
- online/atlas_stations_v28.json SHA256 b121614b0addf69ec4bb3b4b7b8f9f031f773e69c5a35c7ecc58f05bf48b733d.
- Fail closed with an explicit message when the polygon JS fails SRI; reject altered atlas JSON and retain existing safe per-input-coordinates fallback.

## Exact bytes and test
- Input Stage25 loader SHA256 8f44f6dbc9b346dc4142cbea1da1d3db116cd7d6304e861b4bb701b215f2d72e.
- Result loader SHA256 19c9954f3540a52bb6f83f81794b7f3ccf7b8978bf38ed2393666c78ae2af1f5.
- Index SHA256 unchanged a6d3c06bb3197671e2a7e1f3e2043b924a23ee35c76ca4f35ef9d1e1c66a90d8.
- Of the 16 staged files, 15 are byte-identical to Stage25; node syntax checks pass.
- 20 Chromium native-SRI/route scenarios passed: 4 viewport sizes x 2 languages for rain maps, 2 altered resource rejection scenarios, 5 existing module routes x 2 languages. Zero pageerrors in the harness.
- IMPORTANT LIMITATION: browser navigation to any HTTP origin was blocked by the container administrator. Browser page.route supplied the real asset bytes; the native SRI engine verified map JS and atlas JSON. HTML SHA digest was mocked in the harness because about:blank is not a secure origin, with all file digests separately verified by Python. NOT a live cPanel or HTTPS deployment test.

## GIS inventory in the exact archived JS
iran=1, provinces=31, counties=489, basins=54, subbasins=622; station atlas=1,072 distinct station IDs, with no invalid coordinate pairs by elementary range checks. This does NOT establish authoritative administrative validity or connectivity to the five-level main map menu.

## Safe installation
- If Stage25 is ACTIVE and hash matches: install 1-file delta after backup.
- If Stage22 is ACTIVE and hash matches: use the 3-file Stage22 overlay after confirming the six prior module/dependency hashes; do not overwrite divergent newer assets.
- A complete 16-file ZIP exists for staging only. The pinned dependencies are offered separately only if absent and after SHA review.
- Read-only preflight script checks exact active file hashes; stop on mismatch. No deployment has been performed. No file removal has been authorized.

## Remaining roadmap
P1/P2: R5 controls and bilingual UX across all pages; P3: actual engine mounting; P4: global ECMWF/GFS source fusion and AI models; P5: anomalies and scheduled publishing; P6: county select/real GIS and the rain XLSX; P7: PHP installer/security/availability audit.