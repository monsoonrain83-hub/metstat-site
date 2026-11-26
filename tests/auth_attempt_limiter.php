<?php
declare(strict_types=1);
require __DIR__.'/../server/auth/AttemptLimiter.php';
use MetStat\Auth\AttemptLimiter;
function check(bool $ok,string $msg): void {if(!$ok)throw new RuntimeException($msg);}
function db(string $path):PDO{
  $d=new PDO('sqlite:'.$path,null,null,[PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION]);
  $d->exec('PRAGMA busy_timeout=2500');return $d;
}
$now=1800000000;
if(($argv[1]??'')==='worker'){
  $l=new AttemptLimiter(db($argv[2]));
  echo $l->reserve(['shared'=>['window'=>900,'max'=>5]],$now)?'1':'0';
  exit;
}
$p=tempnam(sys_get_temp_dir(),'msrate-');
try{
 $d=db($p);
 $d->exec('CREATE TABLE attempts(k TEXT NOT NULL,ts INTEGER NOT NULL);CREATE INDEX att_k ON attempts(k,ts)');
 $l=new AttemptLimiter($d);
 $scope=['a'=>['window'=>900,'max'=>2]];
 check($l->allowed($scope,$now),'initial read');
 check((int)$d->query('SELECT COUNT(*) FROM attempts')->fetchColumn()===0,'read wrote row');
 check($l->reserve($scope,$now)&&$l->reserve($scope,$now),'first two');
 check(!$l->reserve($scope,$now),'limit exceeded');
 check(!$l->reserve(['b'=>['window'=>900,'max'=>1]]+$scope,$now),'multi-scope should fail');
 check((int)$d->query("SELECT COUNT(*) FROM attempts WHERE k='b'")->fetchColumn()===0,'partial write');
 check($l->reserve($scope,$now+900),'exact window boundary');
 $q=$d->prepare('INSERT INTO attempts VALUES(?,?)');
 for($i=0;$i<3;$i++)$q->execute(['old',$now-86401]);
 check($l->prune($now,2)===2,'bounded prune');
 check((int)$d->query("SELECT COUNT(*) FROM attempts WHERE k='old'")->fetchColumn()===1,'prune count');
 check((int)$d->query("SELECT COUNT(*) FROM attempts WHERE k='a'")->fetchColumn()===3,'prune active');
 try{$l->reserve(['x'=>['window'=>0,'max'=>1]],$now);throw new RuntimeException('invalid input accepted');}catch(InvalidArgumentException){}
 $workers=[];
 for($i=0;$i<20;$i++){
  $proc=proc_open([PHP_BINARY,__FILE__,'worker',$p],[1=>['pipe','w'],2=>['pipe','w']],$pipes);
  check(is_resource($proc),'worker start');$workers[]=[$proc,$pipes];
 }
 $accepted=0;
 foreach($workers as [$proc,$pipes]){
  $out=stream_get_contents($pipes[1]);$err=stream_get_contents($pipes[2]);fclose($pipes[1]);fclose($pipes[2]);
  check(proc_close($proc)===0&&in_array($out,['0','1'],true),'worker error: '.$err);$accepted+=(int)$out;
 }
 check($accepted===5,'concurrent admission');check((int)$d->query("SELECT COUNT(*) FROM attempts WHERE k='shared'")->fetchColumn()===5,'stored count');
 // Locked writer: read still works on separate connection; reservation must not bypass.
 $other=db($p);$other->exec('PRAGMA busy_timeout=30');
 $d->exec('BEGIN IMMEDIATE');
 try{
  $locked=new AttemptLimiter($other);
  check($locked->allowed(['fresh'=>['window'=>900,'max'=>1]],$now),'read under lock');
  try{$locked->reserve(['fresh'=>['window'=>900,'max'=>1]],$now);throw new RuntimeException('lock bypass');}catch(PDOException){}
 }finally{$d->exec('ROLLBACK');}
 check((int)$d->query("SELECT COUNT(*) FROM attempts WHERE k='fresh'")->fetchColumn()===0,'unexpected locked write');
 echo "PASS: read-only, limits, rollback, window, bounded cleanup, validation, 20 concurrent workers / 5 admitted, locked writer fail closed\n";
}finally{@unlink($p);}
