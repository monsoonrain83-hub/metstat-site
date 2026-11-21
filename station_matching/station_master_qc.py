#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit MetStat master points without conflating OSM localities with rain gauges.

Input: MetStat_Master_20261121.csv or a zip containing that file.
Output: station sensor candidate CSV + JSON provenance/QC summary. Neither output
is a declaration that unverified Persian names or locations are confirmed.
"""
from collections import Counter
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import zipfile

STATION_TYPES = frozenset(('synoptic', 'climatology', 'raingauge', 'automatic', 'aws', 'hydrometric'))
REQUIRED = frozenset(('شناسه', 'نام فارسی', 'نام لاتین', 'عرض جغرافیایی', 'طول جغرافیایی',
                      'استان', 'شهرستان', 'نوع نقطه / شبکه', 'منبع', 'وضعیت اعتبار نام'))
OUT_HEADERS = ('شناسه', 'نام فارسی', 'نام لاتین', 'عرض جغرافیایی', 'طول جغرافیایی',
               'استان', 'شهرستان', 'نوع نقطه / شبکه', 'منبع', 'وضعیت اعتبار نام',
               'نقش در جست‌وجو', 'وضعیت QC موقعیت', 'نیازمند بررسی نام')


def open_master(path):
    """Return a UTF-8 TextIOWrapper and a resource for safe closure."""
    f = Path(path)
    if f.suffix.lower() != '.zip':
        raw = f.open('rb')
        return io.TextIOWrapper(raw, encoding='utf-8-sig', newline=''), raw
    zipf = zipfile.ZipFile(f)
    names = [n for n in zipf.namelist() if n.endswith('.csv') and 'Master_' in n and 'Duplicate' not in n]
    if len(names) != 1:
        zipf.close()
        raise ValueError('Expected exactly one master point CSV inside ZIP')
    stream = zipf.open(names[0])
    return io.TextIOWrapper(stream, encoding='utf-8-sig', newline=''), zipf


def validate_coord(row):
    try:
        lat, lon = float(row['عرض جغرافیایی']), float(row['طول جغرافیایی'])
    except (ValueError, TypeError):
        return 'missing_or_nonnumeric'
    if not (24 <= lat <= 41.5 and 43 <= lon <= 65):
        return 'out_of_iran_bbox'
    return 'in_iran_bbox_unverified'


def name_review(row):
    # Documented aliases, transliteration and OSM names are NOT independently verified.
    status = (row.get('وضعیت اعتبار نام') or '').lower()
    return 'خیر' if status in ('confirmed', 'independently_verified') else 'بله'


def audit(input_path, stations_output, summary_output):
    counts = Counter()
    types = Counter()
    statuses = Counter()
    missing = Counter()
    ids = set()
    duplicate_ids = []
    stream, owner = open_master(input_path)
    try:
        reader = csv.DictReader(stream)
        if not REQUIRED.issubset(reader.fieldnames or []):
            raise ValueError('Missing fields: ' + ', '.join(sorted(REQUIRED - set(reader.fieldnames or []))))
        Path(stations_output).parent.mkdir(parents=True, exist_ok=True)
        with open(stations_output, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=OUT_HEADERS, extrasaction='ignore')
            writer.writeheader()
            for row in reader:
                counts['all_points'] += 1
                rid = (row.get('شناسه') or '').strip()
                if not rid or rid in ids:
                    if len(duplicate_ids) < 20: duplicate_ids.append(rid or '(empty)')
                    counts['duplicate_or_missing_id'] += 1
                else:
                    ids.add(rid)
                kind = (row.get('نوع نقطه / شبکه') or '').strip().lower()
                statuses[row.get('وضعیت اعتبار نام') or '(empty)'] += 1
                types[kind] += 1
                if not row.get('نام فارسی', '').strip(): missing['persian_name'] += 1
                if not row.get('استان', '').strip(): missing['province'] += 1
                coord_qc = validate_coord(row)
                if coord_qc != 'in_iran_bbox_unverified': missing['invalid_coordinates'] += 1
                if kind in STATION_TYPES:
                    counts['station_sensor_rows'] += 1
                    output = dict(row)
                    output['نقش در جست‌وجو'] = 'station_candidate'
                    output['وضعیت QC موقعیت'] = coord_qc
                    output['نیازمند بررسی نام'] = name_review(row)
                    writer.writerow(output)
                else:
                    counts['settlement_or_other_rows'] += 1
    finally:
        stream.close()
        owner.close()
    if counts['duplicate_or_missing_id']:
        raise ValueError('Station master has duplicate or missing record IDs: ' + str(duplicate_ids))
    out_sha = hashlib.sha256(Path(stations_output).read_bytes()).hexdigest()
    report = {
        'schema': 'metstat-station-audit-v1',
        'source_file': Path(input_path).name,
        'source_sha256': hashlib.sha256(Path(input_path).read_bytes()).hexdigest(),
        'sensor_candidate_file': Path(stations_output).name,
        'sensor_candidate_sha256': out_sha,
        'counts': dict(counts),
        'missing': dict(missing),
        'types': dict(sorted(types.items())),
        'name_status': dict(sorted(statuses.items())),
        'quality_note': 'Bounding-box coordinates and category identify candidates, NOT independently verified station names. OSM settlements are excluded from sensor candidates.',
        'deployment_status': 'staging_only; not a live station database or final XLSX',
    }
    Path(summary_output).write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True)
    parser.add_argument('--stations-out', required=True)
    parser.add_argument('--report-out', required=True)
    args = parser.parse_args()
    result = audit(args.source, args.stations_out, args.report_out)
    print(json.dumps({'counts': result['counts'], 'missing': result['missing'],
                      'sha256': result['sensor_candidate_sha256']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
