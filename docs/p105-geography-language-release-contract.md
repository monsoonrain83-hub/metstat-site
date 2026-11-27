# P1-05 release constraints (administrator decision, 2026-11-27)

- Preserve the existing Iranian province, county and place datasets byte-for-byte. No geometry replacement, repair, simplification, renaming or coordinate edits. New language labels must be separate, keyed by verified identity.
- Foreign data: preserve source coordinates; no per-feature simplification. Reject new overlaps, gaps and mismatched shared edges. Validate against a reviewed footprint and verified parent IDs. An upstream source conflict must be investigated, not repaired automatically.
- English UI, legends, maps, exports, messages and all modules must contain no Persian-script display text. Persian UI uses verified Persian geographical names, labels, headings and explanations. Official weather-model names remain in English in either locale.
- Do not infer translated geographic names from spelling or proximity alone. Source IDs, country and administrative parent must agree. Missing translations block release of affected new data.
- The P1-03 native nvGeoMenuRows function contains nine Persian string literals and has no locale branch; the surrounding syncGeo localizes headings but not all returned option labels. This is a confirmed code-level defect, not a completed full-site runtime audit.
- P1-04 protected-file audit: all six SHA-256 hashes match the supplied public_html backup. P1-03 candidate ZIP matches the recorded hash f599be26a89181bae493a65a8bdd706d02341c3b93d8372a43061045a8ecae04.
- P1-05 stages Iraq, Japan and United States from pinned geoBoundaries gbOpen revision 8ce2700661a28ee944350e2b329bbabb58d2ff83. Metadata, license and raw LFS payload integrity are captured. No names or boundary-policy approvals are invented.
- Staging artifacts, including failed layer evidence, are NOT production releases. No host credentials, host uploads or main-branch changes. No automatic promotion.
