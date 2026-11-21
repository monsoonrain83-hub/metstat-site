# MetStat station master + v39 rainfall matching QA (2026-11-21)

## Inputs
- `MetStat_Master_57076_Points_20261121.zip` (SHA256 `79265fc4875ba53cb3cc7f38e714d7113e69e01ba7be3ff1c5f6ca3bd4a5ecb2`), `MetStat_Master_20261121.csv`.
- `MetStat_v39_Station_Matching_40_Unresolved_Audit.xlsx` sheets: خلاصه; ۴۰ مورد نامشخص; ۶ شناسه قابل پیگیری.

## Row-level source profile (stdlib CSV, no geocoding)
| Check | Observed |
|---|---:|
| All master records | 57,076 |
| Synoptic | 89 |
| Climatology | 19 |
| Raingauge | 2,602 |
| **Recognized weather station records** | **2,710** |
| Agricultural records (classified separately; NOT auto-approved sensor) | 90 |
| OSM settlements / other (all minus 2710 and 90) | 54,276 |
| Missing Persian names (all in 2,710 recognized station records) | 2,145 |
| Missing station elevations | 2,710 / 2,710 |
| Missing station province | 0 / 2,710 |
| All records missing province | 394 |
| Duplicate IDs among master rows | 0 |
| Invalid coordinates (parse/range) | 0 |
| Outside broad Iran bbox 24–40.5N, 44–64E | 0 |
| Rows in **separate**, precomputed duplicate-audit table | 699 |

**Critical distinction:** Coordinates within a broad national bbox are NOT independent proof that a named station exists at that point. Do not synthesize a station from a same-name village or agricultural place. The 699-row duplicate-audit is not a remaining duplicate-ID count; it records earlier removal decisions requiring provenance review.

Missing Persian names by type: synoptic 16, climatology 17, raingauge 2,112. Proposed spellings are NOT verified aliases; retain evidence and manual review state.

## Rainfall v39 audit
179 input precipitation reports: 139 map-ready, 40 **unresolved** (all from 108 manual entries; 71 automatic 24-hour reports in the ready group). Four of six ID-bearing unresolved entries have same reporting and bank province but need station/site verification; two have hard province conflicts:
- `رودبار` report گیلان vs bank هرمزگان, ID W99317
- `اویهنگ` report کردستان vs bank همدان, ID METAMETA01227

Never auto-accept a numeric ID if province conflicts. Same-name sites at different coordinates cannot be resolved by name alone. Do NOT use an OSM settlement's centroid as a rain-gauge coordinate.

## Actual implemented safety fix
Branch `fix/station-sensor-vs-osm-20261121` updates `station_resolver_v1.js`:
1. Only whitelisted observing-station categories may become verified.
2. Empty lat/lon strings are not interpreted as numeric zero.
3. Out-of-Iran lat/lon cannot become an Iranian station.
4. Existing province/county hard filters and learned-match identity checks remain.
5. 14 existing and new assertions passed in a connector-evaluated JavaScript module test. Private GitHub Actions remain blocked before runner steps.

## To finish production Excel & live database
A final workbook requires explicit confirmed/unverified status and source ID, province/county consistency, alias review and 40-case resolution or clear review flags; do not call a populated OSM name a verified observing site. No final Excel or live database published from these inputs yet.
