"""Offline lossless partition prototype; does not modify the source or host."""
import hashlib
import json
from collections import defaultdict
from pathlib import Path

SECTIONS = ('items', 'items_prev')

def encode(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')

def digest(value):
    return hashlib.sha256(encode(value)).hexdigest()

def partition(manifest):
    if not isinstance(manifest, dict) or not isinstance(manifest.get('models'), dict):
        raise ValueError('missing model metadata')
    meta = {k: v for k, v in manifest.items() if k not in SECTIONS}
    shards = {}
    counts = {}
    for section in SECTIONS:
        rows = manifest.get(section)
        if not isinstance(rows, list):
            raise ValueError('missing list: '+section)
        counts[section] = len(rows)
        groups = defaultdict(list)
        for index, row in enumerate(rows):
            if not isinstance(row, dict) or not isinstance(row.get('m'), str) or row['m'] not in manifest['models']:
                raise ValueError('unknown model in '+section)
            groups[row['m']].append([index, row])
        for model, entries in groups.items():
            shards[(section, model)] = entries
    catalog = {'schema': 1, 'manifest_sha256': digest(manifest), 'metadata': meta, 'counts': counts,
               'shards': [{'section': s, 'model': m, 'rows': len(v), 'sha256': digest(v)} for (s,m), v in sorted(shards.items())],
               'root_order': list(manifest)}
    return catalog, shards

def reconstruct(catalog, shards):
    if catalog.get('schema') != 1:
        raise ValueError('unknown schema')
    out = dict(catalog['metadata'])
    for section in SECTIONS:
        out[section] = [None] * catalog['counts'][section]
    keys = set()
    for spec in catalog['shards']:
        key = (spec['section'], spec['model'])
        if key in keys or key not in shards:
            raise ValueError('duplicate or missing shard')
        keys.add(key)
        rows = shards[key]
        if len(rows) != spec['rows'] or digest(rows) != spec['sha256']:
            raise ValueError('shard integrity mismatch')
        for index, row in rows:
            target = out[key[0]]
            if type(index) is not int or not 0 <= index < len(target) or target[index] is not None or row.get('m') != key[1]:
                raise ValueError('invalid shard position or model')
            target[index] = row
    if keys != set(shards) or any(x is None for s in SECTIONS for x in out[s]):
        raise ValueError('extra or missing rows')
    out = {k: out[k] for k in catalog['root_order']}
    if digest(out) != catalog['manifest_sha256']:
        raise ValueError('manifest digest mismatch')
    return out

def report(manifest):
    catalog, shards = partition(manifest)
    assert reconstruct(catalog, shards) == manifest
    return {'rows': catalog['counts'], 'shard_count': len(shards), 'source_bytes': len(encode(manifest)), 'catalog_bytes': len(encode(catalog)), 'current_bytes': len(encode(manifest['items'])), 'previous_bytes': len(encode(manifest['items_prev'])), 'roundtrip_sha256': catalog['manifest_sha256'], 'model_bytes': {m: {s: len(encode(v)) for (s, k), v in shards.items() if k == m} for m in manifest['models']}}

if __name__ == '__main__':
    import sys
    print(json.dumps(report(json.loads(Path(sys.argv[1]).read_bytes())), indent=2, ensure_ascii=False))
