# -*- coding: utf-8 -*-
import csv
import tempfile
import unittest
import zipfile
from pathlib import Path
from station_matching.station_master_qc import audit, validate_coord, name_review

HEADER=['شناسه','نام فارسی','نام لاتین','عرض جغرافیایی','طول جغرافیایی',
        'استان','شهرستان','نوع نقطه / شبکه','منبع','وضعیت اعتبار نام']


class MasterAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.csv=self.root/'MetStat_Master_20261121.csv'
        self.out=self.root/'sensor.csv'
        self.report=self.root/'report.json'

    def write_rows(self, rows):
        with self.csv.open('w',encoding='utf-8-sig',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=HEADER)
            writer.writeheader()
            writer.writerows(rows)

    def row(self, id, kind, name, status='proposal_unverified'):
        return dict(zip(HEADER,[id,name,id,'36.2','58.9','خراسان رضوی',
                                'نیشابور',kind,'synthetic',status]))

    def test_excludes_village_from_sensor_output(self):
        self.write_rows([self.row('s-1','raingauge','بوژان'),
                         self.row('o-1','village','بوژان')])
        rep=audit(self.csv,self.out,self.report)
        self.assertEqual(rep['counts']['station_sensor_rows'],1)
        self.assertEqual(rep['counts']['settlement_or_other_rows'],1)
        with self.out.open(encoding='utf-8-sig') as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['شناسه'],'s-1')
        self.assertEqual(rows[0]['نیازمند بررسی نام'],'بله')
        self.assertEqual(len(rep['sensor_candidate_sha256']),64)

    def test_zip_path_really_reads_master_only(self):
        self.write_rows([self.row('s1','synoptic','رشت',status='confirmed')])
        p=self.root/'test.zip'
        with zipfile.ZipFile(p,'w') as z:
            z.write(self.csv,arcname=self.csv.name)
            z.writestr('noise.csv','irrelevant')
        rep=audit(p,self.out,self.report)
        self.assertEqual(rep['counts']['all_points'],1)
        with self.out.open(encoding='utf-8-sig') as f:
            self.assertEqual(list(csv.DictReader(f))[0]['نیازمند بررسی نام'],'خیر')

    def test_invalid_coordinates_are_reported_not_autofixed(self):
        row=self.row('s-1','raingauge','نام')
        row['عرض جغرافیایی']=''
        self.write_rows([row])
        report=audit(self.csv,self.out,self.report)
        self.assertEqual(report['missing']['invalid_coordinates'],1)
        self.assertEqual(validate_coord(row),'missing_or_nonnumeric')
        self.assertEqual(name_review(row),'بله')

    def test_duplicate_source_ids_fail_closed(self):
        self.write_rows([self.row('s1','raingauge','بوژان'),
                         self.row('s1','village','بوژان')])
        with self.assertRaisesRegex(ValueError,'duplicate'):
            audit(self.csv,self.out,self.report)


if __name__=='__main__':
    unittest.main()
