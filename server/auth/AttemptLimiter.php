<?php
declare(strict_types=1);
namespace MetStat\Auth;

use PDO;
use InvalidArgumentException;
use LogicException;

/**
 * Candidate for the existing attempts(k,ts) schema. Not wired to production.
 * All errors propagate so callers must fail closed (503), never bypass limits.
 * No request-path cleanup or DDL; use a separately scheduled maintenance job.
 */
final class AttemptLimiter {
    public function __construct(private PDO $db) {
        if ($db->getAttribute(PDO::ATTR_DRIVER_NAME) !== 'sqlite' ||
            $db->getAttribute(PDO::ATTR_ERRMODE) !== PDO::ERRMODE_EXCEPTION) {
            throw new InvalidArgumentException('SQLite with exception mode required');
        }
    }

    /** @param array<string,array{window:int,max:int}> $scopes */
    private function validate(array $scopes, int $now): void {
        if (!$scopes || count($scopes)>8 || $now<86400) throw new InvalidArgumentException('invalid scopes/time');
        foreach ($scopes as $key=>$spec) {
            if (!is_string($key) || strlen($key)<1 || strlen($key)>256 ||
                !is_array($spec) || !is_int($spec['window']??null) || !is_int($spec['max']??null) ||
                $spec['window']<1 || $spec['window']>86400 || $spec['max']<1 || $spec['max']>10000) {
                throw new InvalidArgumentException('invalid limit');
            }
        }
    }

    /** Atomically reserve one attempt per scope, or reserve none. */
    public function reserve(array $scopes, int $now): bool {
        $this->validate($scopes,$now);
        if ($this->db->inTransaction()) throw new LogicException('caller transaction not supported');
        $started=false;
        try {
            $this->db->exec('BEGIN IMMEDIATE'); $started=true;
            $q=$this->db->prepare('SELECT COUNT(*) FROM attempts WHERE k=? AND ts>?');
            foreach ($scopes as $key=>$spec) {
                $q->execute([$key,$now-$spec['window']]);
                $n=(int)$q->fetchColumn(); $q->closeCursor();
                if ($n >= $spec['max']) {
                    $this->db->exec('ROLLBACK'); $started=false; return false;
                }
            }
            $q=$this->db->prepare('INSERT INTO attempts(k,ts) VALUES(?,?)');
            foreach ($scopes as $key=>$spec) $q->execute([$key,$now]);
            $this->db->exec('COMMIT'); $started=false; return true;
        } finally {
            if ($started) $this->db->exec('ROLLBACK');
        }
    }

    /** Read-only observation, not sufficient for concurrent admission. */
    public function allowed(array $scopes, int $now): bool {
        $this->validate($scopes,$now);
        $q=$this->db->prepare('SELECT COUNT(*) FROM attempts WHERE k=? AND ts>?');
        foreach ($scopes as $key=>$spec) {
            $q->execute([$key,$now-$spec['window']]);
            $n=(int)$q->fetchColumn(); $q->closeCursor();
            if ($n >= $spec['max']) return false;
        }
        return true;
    }

    /** Maintenance only. At most 1000 rows per call; retention >= max supported window. */
    public function prune(int $now, int $limit=250): int {
        if ($now<86400 || $limit<1 || $limit>1000) throw new InvalidArgumentException('invalid prune range');
        $q=$this->db->prepare('DELETE FROM attempts WHERE rowid IN (SELECT rowid FROM attempts WHERE ts<=? ORDER BY ts,rowid LIMIT ?)');
        $q->bindValue(1,$now-86400,PDO::PARAM_INT);
        $q->bindValue(2,$limit,PDO::PARAM_INT);
        $q->execute(); return $q->rowCount();
    }
}
