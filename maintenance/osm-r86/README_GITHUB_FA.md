# MetStat OSM r86 — staged source only

Read `INSTALL_QA_FA.md` before deploying. This branch is based on PR #4 (r85 UI). It does not deploy automatically to cPanel and does not alter the private station AES-GCM registry.

The generated OSM gazetteer shards (257 files) are distributed as versioned installation archives; the 2,304-peak JSON and administrative polygons are versioned in this branch in the ChatGPT deliverable. They are derived from the user's PBF-extracted Excel; see the build scripts, site GIS polygon overlay and attribution/license instructions.

Run: `python build_osm_geo.py iran_osm_nodes_database.xlsx ./generated`; `python enrich_admin_gis.py` (requires admin polygon file and matching working directory); `python build_osm_shards.py generated/osm_geonames_v86.sqlite generated/osm_places_shards_v86`; then tests.
