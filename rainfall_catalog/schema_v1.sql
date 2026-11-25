-- Independent rainfall catalog prototype; do not run against Atlas or production.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS source (
  id TEXT PRIMARY KEY, name TEXT NOT NULL, version TEXT, license TEXT, imported_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS location (
  id TEXT PRIMARY KEY,
  kind TEXT NOT NULL CHECK(kind IN ('station','place')),
  name_fa TEXT NOT NULL CHECK(length(trim(name_fa))>0),
  name_en TEXT, latin_status TEXT NOT NULL DEFAULT 'unknown' CHECK(latin_status IN ('verified','generated','unknown')),
  province TEXT, county TEXT, province_code TEXT, county_code TEXT,
  latitude REAL CHECK(latitude BETWEEN 24 AND 41), longitude REAL CHECK(longitude BETWEEN 43 AND 64),
  elevation_m REAL, elevation_source TEXT CHECK(elevation_source IN ('station','dem','other')),
  coordinate_kind TEXT NOT NULL CHECK(coordinate_kind IN ('sensor_verified','sensor_unverified','place_reference','unknown')),
  network TEXT,
  precip_capable INTEGER NOT NULL DEFAULT 0 CHECK(precip_capable IN (0,1)),
  review_state TEXT NOT NULL DEFAULT 'pending' CHECK(review_state IN ('pending','verified','conflict')),
  CHECK((latitude IS NULL)=(longitude IS NULL)),
  CHECK((elevation_m IS NULL)=(elevation_source IS NULL)),
  CHECK(kind='station' OR (precip_capable=0 AND coordinate_kind IN ('place_reference','unknown'))),
  CHECK(coordinate_kind<>'sensor_verified' OR (kind='station' AND latitude IS NOT NULL AND longitude IS NOT NULL))
);
CREATE TABLE IF NOT EXISTS source_record (
  source_id TEXT NOT NULL REFERENCES source(id), source_record_id TEXT NOT NULL,
  location_id TEXT NOT NULL REFERENCES location(id), original_name_fa TEXT, original_name_en TEXT,
  original_lat REAL, original_lon REAL, original_elevation_m REAL, evidence_ref TEXT,
  PRIMARY KEY(source_id,source_record_id)
);
CREATE TABLE IF NOT EXISTS alias (
  location_id TEXT NOT NULL REFERENCES location(id), alias TEXT NOT NULL,
  normalized TEXT NOT NULL, language TEXT NOT NULL CHECK(language IN ('fa','en','other')),
  source_id TEXT NOT NULL REFERENCES source(id),
  status TEXT NOT NULL CHECK(status IN ('verified','candidate')),
  PRIMARY KEY(location_id,normalized,language,source_id)
);
CREATE INDEX IF NOT EXISTS alias_search ON alias(normalized,language);
CREATE INDEX IF NOT EXISTS location_scope ON location(province_code,county_code,kind);
CREATE TABLE IF NOT EXISTS identity_link (
  left_id TEXT NOT NULL REFERENCES location(id), right_id TEXT NOT NULL REFERENCES location(id),
  relation TEXT NOT NULL CHECK(relation IN ('same_sensor','colocated','nearby','possible_duplicate')),
  evidence_ref TEXT NOT NULL, reviewed_by TEXT, reviewed_at TEXT,
  CHECK(left_id<>right_id), PRIMARY KEY(left_id,right_id,relation),
  CHECK(relation<>'same_sensor' OR (reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL))
);
CREATE VIEW IF NOT EXISTS eligible_precip_location AS
SELECT l.* FROM location l
WHERE l.kind='station' AND l.precip_capable=1 AND l.coordinate_kind='sensor_verified'
AND l.review_state='verified' AND l.latitude IS NOT NULL AND l.longitude IS NOT NULL
AND l.province IS NOT NULL AND length(trim(l.province))>0
AND EXISTS (SELECT 1 FROM source_record r WHERE r.location_id=l.id AND r.evidence_ref IS NOT NULL AND length(trim(r.evidence_ref))>0);
-- This view establishes catalog eligibility only; query identity must also be resolved before mapping.
