<?php
declare(strict_types=1);
/* Public-data OSM locality fallback. NEVER describes OSM settlement coordinates as a weather sensor.
 * Requires PHP 7.4+; no PDO/SQLite extension, no private encryption key.
 * JSON shards reside outside public_html, and only bounded query results are returned.
 */
header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');
header('Cache-Control: private, no-store');
function respond(int $status, array $data): void { http_response_code($status); echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_INVALID_UTF8_SUBSTITUTE); exit; }
$home = dirname(__DIR__, 2);
$private = getenv('METSTAT_STATION_PRIVATE_DIR') ?: ($home . '/metstat_station_private');
$folder = rtrim($private,'/') . '/osm_places_shards_v86';
if ($_SERVER['REQUEST_METHOD'] === 'GET' && ($_GET['a'] ?? '') === 'status') {
  respond(200, ['ok'=>true,'version'=>'86','ready'=>is_file($folder.'/_manifest.json'),'source'=>'OpenStreetMap nodes (not a weather station network)']);
}
if ($_SERVER['REQUEST_METHOD'] !== 'POST') respond(405,['ok'=>false,'error'=>'POST required']);
if (!is_file($folder.'/_manifest.json')) respond(503,['ok'=>false,'error'=>'OSM name shards are not installed outside public_html']);
$len=(int)($_SERVER['CONTENT_LENGTH'] ?? 0);
if ($len>65536) respond(413,['ok'=>false,'error'=>'Query batch too large']);
$data=json_decode(file_get_contents('php://input',false,null,0,65537),true);
if (!is_array($data) || !isset($data['queries']) || !is_array($data['queries']) || count($data['queries'])>60) respond(400,['ok'=>false,'error'=>'Expected queries[1..60]']);
function norm_name(string $s): string {
  $s=trim(strtr($s,['ي'=>'ی','ك'=>'ک','ۀ'=>'ه',"\u{200C}"=>' ']));
  $s=preg_replace('/\p{Mn}+/u','',$s) ?? $s;
  $s=preg_replace('/[^\p{L}\p{N}_ ]+/u',' ',$s) ?? $s;
  return strtolower(trim(preg_replace('/\s+/u',' ',$s) ?? $s));
}
$lookup=[];$results=[];
foreach($data['queries'] as $entry){
  if (!is_array($entry)) $entry=['name'=>''];
  $raw=trim((string)($entry['name']??''));
  $key=norm_name($raw);
  if (strlen($key)<3 || strlen($key)>240) { $results[]=['name'=>$raw,'status'=>'invalid','places'=>[]];continue; }
  $shard=substr(sha1($key),0,2);
  if(!array_key_exists($shard,$lookup)){
    $file=$folder.'/'.$shard.'.json';
    $lookup[$shard]=is_file($file)?json_decode(file_get_contents($file),true):[];
    if(!is_array($lookup[$shard])) $lookup[$shard]=[];
  }
  $hit=$lookup[$shard][$key] ?? [];
  $requestedProvince=norm_name((string)($entry['province']??''));
  $requestedCounty=norm_name((string)($entry['county']??''));
  $adminFiltered=[];
  foreach ($hit as $v) {
    if (!is_array($v)||count($v)<12) continue;
    // For an explicitly reported province/county, a missing GIS assignment is NOT proof of membership.
    if ($requestedProvince!=='' && norm_name((string)($v[9]??''))!==$requestedProvince) continue;
    if ($requestedCounty!=='' && norm_name((string)($v[10]??''))!==$requestedCounty) continue;
    $adminFiltered[]=$v;
  }
  $hits=[];
  foreach(array_slice($adminFiltered,0,25) as $v){
    $hits[]=['id'=>'osm-node-'.$v[0],'fa'=>$v[2]?:$v[1],'en'=>$v[3],
      'name'=>$v[1],'lat'=>$v[4],'lon'=>$v[5],
      'type'=>'geographic_reference','geographic_category'=>$v[6],'geographic_subtype'=>$v[7],
      'elev'=>$v[8], 'province_hint'=>$v[9],'county_hint'=>$v[10],
      'osm_url'=>$v[11],'source'=>'OpenStreetMap node; GIS administrative assignment where available','score'=>1.0,
      'approximate'=>true,'requires_review'=>true,'unverified'=>true,'auto_match_allowed'=>false,
      'source_status'=>'osm_geographic_reference_not_sensor'];
  }
  $results[]=['name'=>$raw,'status'=>count($adminFiltered)>25?'ambiguous-truncated':(count($hits)?'geographic-candidates':'not-found'), 'places'=>$hits,'total_exact_osm_nodes'=>count($hit),'within_reported_admin'=>count($adminFiltered)];
}
respond(200,['ok'=>true,'version'=>'86','results'=>$results,'notice'=>'OSM coordinates indicate a geographic name; they do not establish the meteorological instrument location']);
