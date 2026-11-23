<?php
declare(strict_types=1);
/* MetStat opt-in geolocation fallback for ambiguous/unmatched station labels.
 * PHP 7.4+. Input is a NAME, never required lat/lon. Google key remains server-side.
 * Local gazetteer source: sajaddp/list-of-cities-in-Iran GPL-3.0; towns != sensors.
 */
header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');
header('Cache-Control: no-store');
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); echo json_encode(['status'=>'error','reason'=>'POST required']); exit; }
function reply(array $a, int $status=200): void {http_response_code($status);echo json_encode($a,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);exit;}
function nfa($s): string {
    $s=trim(strtr((string)$s,['ي'=>'ی','ى'=>'ی','ك'=>'ک','أ'=>'ا','إ'=>'ا','ؤ'=>'و','ئ'=>'ی','آ'=>'ا','ة'=>'ه','ۀ'=>'ه']));
    $s=preg_replace('/[\x{064B}-\x{065F}\x{0670}\x{06D6}-\x{06ED}]/u','',$s);
    $s=preg_replace('/[\x{200C}\x{200D}_#\.\/،,؛:()\[\]{}\-]/u',' ',$s);
    return preg_replace('/\s+/u',' ',$s) ?? $s;
}
function adminMatch(string $wanted, string $found): bool {
    $w=nfa($wanted);$f=nfa($found);
    if ($w==='') return true;
    return $f===$w || $f==='استان '.$w || $f==='شهرستان '.$w || $f===$w.' استان' || $f===$w.' شهرستان';
}
function fetchGoogle(string $url): ?array {
    if (function_exists('curl_init')) {
        $ch=curl_init($url);
        curl_setopt_array($ch,[CURLOPT_RETURNTRANSFER=>true,CURLOPT_TIMEOUT=>9,CURLOPT_CONNECTTIMEOUT=>4,CURLOPT_FOLLOWLOCATION=>false,CURLOPT_SSL_VERIFYPEER=>true]);
        $raw=curl_exec($ch);$http=curl_getinfo($ch,CURLINFO_HTTP_CODE);curl_close($ch);
        return $raw!==false && $http===200 ? json_decode($raw,true) : null;
    }
    $ctx=stream_context_create(['http'=>['timeout'=>9,'follow_location'=>0],'ssl'=>['verify_peer'=>true,'verify_peer_name'=>true]]);
    $raw=@file_get_contents($url,false,$ctx);
    return $raw===false ? null : json_decode($raw,true);
}
function extractAdmin(array $result, string $type): string {
    foreach ($result['address_components'] ?? [] as $c)
        if (in_array($type,$c['types']??[],true)) return (string)($c['long_name']??'');
    return '';
}
function hasName(string $name,array $r):bool {
    $wanted=nfa($name);
    foreach ($r['address_components']??[] as $c)
        if (adminMatch($wanted,(string)($c['long_name']??'')) || adminMatch($wanted,(string)($c['short_name']??''))) return true;
    $full=nfa((string)($r['formatted_address']??''));
    // A quoted locality name must be present as an entire comma-separated component.
    foreach (preg_split('/[,،]/u',$full) as $part) if(adminMatch($wanted,trim($part)))return true;
    return false;
}
function limitSearch(): bool {
    // Backend-only cost guard; lock protects concurrent requests across workers.
    $p=sys_get_temp_dir().'/metstat_geo_rate_'.hash('sha256',(string)($_SERVER['REMOTE_ADDR']??'')).'.json';
    $fh=@fopen($p,'c+');if(!$fh)return false;
    if(!flock($fh,LOCK_EX)){fclose($fh);return false;}
    $raw=stream_get_contents($fh);$arr=json_decode($raw?:'[]',true);if(!is_array($arr))$arr=[];
    $now=time();$arr=array_values(array_filter($arr,static function($x)use($now){return is_int($x) && $x>$now-60;}));
    $okay=count($arr)<90;
    if($okay)$arr[]=$now;
    ftruncate($fh,0);rewind($fh);fwrite($fh,json_encode($arr));fflush($fh);flock($fh,LOCK_UN);fclose($fh);
    return $okay;
}
$raw=file_get_contents('php://input');
if(strlen((string)$raw)>4096)reply(['status'=>'error','reason'=>'Payload too large'],413);
$d=json_decode((string)$raw,true);
if(!is_array($d))reply(['status'=>'error','reason'=>'Malformed JSON'],400);
$name=trim((string)($d['name']??''));$province=trim((string)($d['province']??''));$county=trim((string)($d['county']??''));
foreach ([$name,$province,$county] as $value)if(strlen($value)>220)reply(['status'=>'error','reason'=>'Invalid text length'],400);
if($name==='')reply(['status'=>'error','reason'=>'Name is required'],400);
$dataDir=dirname(__DIR__).'/data/iran_places';
$provinceFile=$dataDir.'/provinces.json';
$provinces=@json_decode((string)@file_get_contents($provinceFile),true);
if(!is_array($provinces))reply(['status'=>'unavailable','reason'=>'Local gazetteer not installed'],503);
$matches=[];$ids=[];
foreach($provinces as $id=>$p)if($province==='' || adminMatch($province,(string)$p))$ids[]=$id;
foreach($ids as $id) {
   $file=$dataDir.'/p_'.(string)$id.'.json';
   $src=@json_decode((string)@file_get_contents($file),true);
   $entries=$src['names'][nfa($name)]??[];
   foreach($entries as $entry) {
     if($county!==''&&!adminMatch($county,(string)($entry['county']??'')))continue;
     $matches[]=['name'=>$entry['name'],'county'=>$entry['county'],'province'=>$provinces[$id],
       'id'=>$entry['id'],'type'=>$entry['type'],'source'=>'iran_gazetteer'];
   }
}
// Internal gazetteer is for administration/name evidence; it has no village coordinates.
// Infer locality only from a UNIQUE exact match; never override supplied province/county.
if(count($matches)===1) {
   if($province==='')$province=$matches[0]['province'];
   if($county==='')$county=$matches[0]['county'];
}
$key=trim((string)(getenv('METSTAT_GOOGLE_GEOCODING_KEY')?:''));
if($key==='')reply(['status'=>'unavailable','reason'=>'Geocoding provider is not configured','places'=>$matches,
                    'county'=>$county,'province'=>$province]);
if(!limitSearch())reply(['status'=>'unavailable','reason'=>'Geo lookup rate limit reached','places'=>$matches],429);
$address=implode(', ',array_filter([$name,$county,$province,'Iran']));
$url='https://maps.googleapis.com/maps/api/geocode/json?'.http_build_query(['address'=>$address,'language'=>'fa','region'=>'ir','components'=>'country:IR','key'=>$key]);
$google=fetchGoogle($url);
if(!is_array($google) || ($google['status']??'')!=='OK')reply(['status'=>'not_found','reason'=>'Geocoder returned no usable result','places'=>$matches]);
$candidates=[];
foreach($google['results']??[] as $g) {
  if(($g['partial_match']??false)===true || !hasName($name,$g))continue;
  $p=extractAdmin($g,'administrative_area_level_1');
  $c=extractAdmin($g,'administrative_area_level_2');
  if($province!=='' && ($p==='' || !adminMatch($province,$p))) continue;
  if($county!=='' && ($c==='' || !adminMatch($county,$c))) continue;
  $lat=$g['geometry']['location']['lat']??null;$lon=$g['geometry']['location']['lng']??null;
  if(!is_numeric($lat)||!is_numeric($lon))continue;
  if($lat<24||$lat>41||$lon<43||$lon>64)continue;
  $candidates[]=['name'=>$name,'lat'=>(float)$lat,'lon'=>(float)$lon,'province'=>$p,'county'=>$c,
     'source'=>'google_geocoding','station_type'=>'geographic_reference','admin_verified'=>true,'unique'=>false,
     'not_sensor'=>true,'accuracy'=>'location_reference'];
}
// Ambiguous coordinates remain unresolved; exact locality without geographic confidence also remains unresolved.
if(count($candidates)===1){$candidates[0]['unique']=true;reply(['status'=>'exact']+$candidates[0]);}
if(count($candidates)>1)reply(['status'=>'ambiguous','reason'=>'Multiple geocoded locations','candidates'=>$candidates]);
reply(['status'=>'not_found','reason'=>'No name-and-administration-consistent coordinate','places'=>$matches]);
