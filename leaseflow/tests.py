import csv,json,shutil,sqlite3,tempfile,threading,unittest,urllib.request,urllib.error
from pathlib import Path
from unittest.mock import patch
from http.server import ThreadingHTTPServer
import pipeline
from pipeline import ROOT,CONTRACTS,ingest,connect,session,snapshot
from app import make_handler

class PipelineTests(unittest.TestCase):
 def setUp(self):
  (ROOT/'tmp').mkdir(exist_ok=True);self.temp=tempfile.TemporaryDirectory(dir=ROOT/'tmp');self.folder=Path(self.temp.name).resolve();assert self.folder.is_relative_to((ROOT/'tmp').resolve())
  self.input=self.folder/'input';shutil.copytree(ROOT/'fixtures',self.input);self.db=self.folder/'warehouse.db'
 def tearDown(self):self.temp.cleanup()
 def run_pipeline(self):return ingest(self.input,self.db)
 def rows(self,source):
  with (self.input/(source+'.csv')).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
 def write(self,source,rows):
  with (self.input/(source+'.csv')).open('w',newline='',encoding='utf-8') as f:
   writer=csv.DictWriter(f,fieldnames=CONTRACTS[source]['columns']);writer.writeheader();writer.writerows(rows)
 def query(self,sql,params=()):
  with session(self.db) as conn:return [dict(r) for r in conn.execute(sql,params)]
 def test_fixture_counts_and_quality_accounting(self):
  result=self.run_pipeline();self.assertEqual({k:result[k] for k in ['read','inserted','quarantined','duplicate']},{'read':21,'inserted':13,'quarantined':7,'duplicate':1});self.assertEqual(sum(result[k] for k in ['inserted','updated','unchanged','stale','duplicate','quarantined']),result['read']);self.assertEqual(len(snapshot(self.db)['issues']),8)
 def test_rerun_has_zero_curated_writes_and_stable_raw_records(self):
  self.run_pipeline();repeat=self.run_pipeline();self.assertEqual(repeat['inserted']+repeat['updated'],0);self.assertEqual(repeat['unchanged'],13);self.assertEqual(len(self.query('SELECT * FROM bronze_records')),20);self.assertEqual(len(self.query('SELECT * FROM issues')),8)
 def test_foreign_key_failures_do_not_enter_curated_tables(self):
  self.run_pipeline();self.assertFalse(self.query('SELECT * FROM leases WHERE lease_id=?',('L005',)));self.assertFalse(self.query('SELECT * FROM payments WHERE payment_id=?',('E007',)));self.assertEqual(len(self.query("SELECT * FROM issues WHERE rule='foreign_key'")),2)
 def test_late_event_is_accepted_using_record_update_version(self):
  self.run_pipeline();row=self.query('SELECT * FROM payments WHERE payment_id=?',('E005',))[0];self.assertEqual(row['paid_at'],'2026-09-15');self.assertTrue(row['updated_at'].startswith('2026-10-10'))
 def test_newer_version_updates_once_and_refreshes_sql_aggregates(self):
  self.run_pipeline();rows=self.rows('payments');rows[0].update(amount_cents='250000',updated_at='2026-10-20T10:00:00Z');self.write('payments',rows);result=self.run_pipeline();self.assertEqual(result['updated'],1);self.assertEqual(self.query('SELECT SUM(payment_amount_cents) AS total FROM mart_property_summary')[0]['total'],1150000);self.assertEqual(self.run_pipeline()['updated'],0)
 def test_older_version_cannot_overwrite_newer_value(self):
  self.run_pipeline();rows=self.rows('payments');rows[0].update(amount_cents='1',updated_at='2026-09-01T10:00:00Z');self.write('payments',rows);self.assertEqual(self.run_pipeline()['stale'],1);self.assertEqual(self.query("SELECT amount_cents FROM payments WHERE payment_id='E001'")[0]['amount_cents'],240000)
 def test_equal_version_conflict_is_quarantined(self):
  self.run_pipeline();rows=self.rows('payments');rows[0]['amount_cents']='1';self.write('payments',rows);self.assertEqual(self.run_pipeline()['quarantined'],8);self.assertTrue(self.query("SELECT * FROM issues WHERE rule='version_conflict'"));self.assertEqual(self.query("SELECT amount_cents FROM payments WHERE payment_id='E001'")[0]['amount_cents'],240000)
 def test_schema_drift_fails_without_modifying_warehouse(self):
  self.run_pipeline();before=snapshot(self.db);file=self.input/'payments.csv';file.write_text(file.read_text().replace('amount_cents','amount_dollars'),encoding='utf-8');self.assertRaisesRegex(ValueError,'Schema drift',self.run_pipeline);after=snapshot(self.db);self.assertEqual(before['counts'],after['counts']);self.assertEqual(after['runs'][0]['status'],'failed');self.assertEqual(len(before['issues']),len(after['issues']))
 def test_mid_run_failure_rolls_back_all_curated_and_bronze_writes(self):
  self.run_pipeline();rows=self.rows('properties');rows.append({'property_id':'P099','city':'Demo','state':'NY','unit_count':'10','updated_at':'2026-10-10T10:00:00Z'});self.write('properties',rows);original=pipeline.validate
  def fail_on_lease(source,*args):
   if source=='leases':raise RuntimeError('Injected stage failure')
   return original(source,*args)
  with patch('pipeline.validate',side_effect=fail_on_lease):self.assertRaisesRegex(RuntimeError,'Injected',self.run_pipeline)
  self.assertFalse(self.query("SELECT * FROM properties WHERE property_id='P099'"));self.assertEqual(len(self.query('SELECT * FROM bronze_records')),20);self.assertEqual(self.query('SELECT status FROM runs ORDER BY rowid DESC LIMIT 1')[0]['status'],'failed')
 def test_gold_totals_avoid_payment_lease_join_fanout(self):
  self.run_pipeline();totals=self.query('SELECT SUM(lease_count) AS leases,SUM(monthly_rent_cents) AS rent,SUM(payment_amount_cents) AS paid FROM mart_property_summary')[0];self.assertEqual(totals,{'leases':4,'rent':1040000,'paid':1140000});self.assertEqual(self.query('SELECT SUM(payment_amount_cents) AS paid FROM mart_property_day')[0]['paid'],1140000)
 def test_integer_cents_and_valid_lease_dates_are_enforced(self):
  self.run_pipeline();self.assertFalse(self.query("SELECT * FROM leases WHERE lease_id IN ('L006','L007')"));self.assertFalse(self.query("SELECT * FROM payments WHERE payment_id IN ('E006','E008')"));self.assertEqual(self.query("SELECT typeof(amount_cents) AS type FROM payments LIMIT 1")[0]['type'],'integer')
 def test_timezone_normalization_retains_fractional_version_precision(self):
  self.assertEqual(pipeline.timestamp('2026-10-01T11:00:00.123456+02:00'),'2026-10-01T09:00:00.123456+00:00');self.assertRaises(ValueError,pipeline.timestamp,'2026-10-01T09:00:00')
 def test_source_values_are_parameterized_not_executed(self):
  rows=self.rows('properties');rows[0]['city']="Demo'); DROP TABLE properties; --";self.write('properties',rows);self.run_pipeline();self.assertEqual(len(self.query('SELECT * FROM properties')),3);self.assertIn('DROP TABLE',self.query("SELECT city FROM properties WHERE property_id='P001'")[0]['city'])

class ApiTests(unittest.TestCase):
 setUp=PipelineTests.setUp
 tearDown=PipelineTests.tearDown
 run_pipeline=PipelineTests.run_pipeline
 def test_data_app_supports_note_crud_and_reports_errors(self):
  self.run_pipeline();server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(self.db));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}'
  def request(path,method='GET',body=None,origin=None):
   headers={'Content-Type':'application/json'}
   if origin:headers['Origin']=origin
   req=urllib.request.Request(base+path,data=json.dumps(body).encode() if body is not None else None,method=method,headers=headers)
   with urllib.request.urlopen(req,timeout=5) as response:return json.load(response)
  try:
   overview=request('/api/overview');issue_id=overview['issues'][0]['issue_id'];created=request('/api/notes','POST',{'issue_id':issue_id,'text':'Investigating source mapping'});self.assertGreater(created['note_id'],0)
   updated=request('/api/notes/'+str(created['note_id']),'PATCH',{'text':'Source mapping reviewed'});self.assertEqual(updated['text'],'Source mapping reviewed');self.assertEqual(len(request('/api/notes')),1)
   request('/api/notes/'+str(created['note_id']),'DELETE');self.assertEqual(request('/api/notes'),[])
   with self.assertRaises(urllib.error.HTTPError) as error:request('/api/notes','POST',{'issue_id':'unknown','text':'x'})
   self.assertEqual(error.exception.code,400)
   with self.assertRaises(urllib.error.HTTPError) as error:request('/api/notes','POST',{'issue_id':issue_id,'text':'x'},'https://example.com')
   self.assertEqual(error.exception.code,403)
   with self.assertRaises(urllib.error.HTTPError) as error:request('/var/warehouse.db')
   self.assertEqual(error.exception.code,404)
  finally:server.shutdown();server.server_close();thread.join(timeout=3)

if __name__=='__main__':unittest.main(verbosity=2)
