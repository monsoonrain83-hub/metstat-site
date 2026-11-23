# MetStat R5 / R9.6 stage 15: measured geometry repair (review only)

Scope: uploaded staged R9.6 index.html with compatible R201 asset; this is NOT an authenticated copy of active cPanel files. No website deployment.

## Confirmed staging problems
- At logical 960px, nav button 7 began at x=166 while its viewport began at x=200, so it was horizontally clipped.
- When a model image is missing, the uninitialized HTML canvas defaults to a 300x150 bitmap; stretching it to 606px width produced a 303px blank colorbar and displaced the timeline ~337px below the map.
- In 844x390 mobile fullscreen, the previous landscape fix still provided a 335px map; this patch does not change fullscreen logic.

## Minimal fix
1. Edit existing R9 nav flex gap 5px to 3px.
2. Shorten the actual composer group label to «نقشه‌های آنلاین و آفلاین», preserving its key, descendants, routes and handlers.
3. Add width=600 height=44 attributes to the existing canvas nvLg, so empty state does not create a giant placeholder. Existing nvLegend() still dynamically sets bitmap size and CSS height when a valid frame is selected.

## Exact source identity
Input index SHA256: 52e16fb3afbcd5e6e571fa8a42e939d03e3274a1925cdc48a47085e3f17de881
After patch SHA256: 754b8345c3c30cf2ef10c456345ea0d6cc5e9ad5e6997d4597b33796e9d9f9b3

The patch successfully passed patch -p1 --dry-run against this exact uploaded input copy. Do not apply to any different index without a three-way diff and user review.

## Real-browser QA (Chromium; synthetic NWP manifest, NOT live data)
390x844 portrait: BEFORE fail nav, colorbar, timeline; AFTER pass.
844x390 landscape: BEFORE fail nav, colorbar, timeline; AFTER pass.
960x720 desktop: BEFORE fail nav, colorbar, timeline; AFTER pass.
1440x900 desktop: BEFORE fail colorbar and timeline; AFTER pass.
At logical width 960, blank legend 303 -> 44 CSS px and map-to-timeline gap 337 -> 78 CSS px.

The offline gate checks 7 nav buttons, mobile logical canvas fitted to viewport, right control column, map/canvas/timeline geometry, map tool buttons, fullscreen enter/exit and duplicate DOM IDs.

Limitations: real server manifest, login, GIS extents, model source availability, data tiles and other pages have NOT been verified. No release is approved. Before deployment, obtain actual cPanel ACTIVE files and backup both index and R201 asset, compare hashes, test and get administrator approval. Never invoke legacy automatic site deployment for this draft review.
