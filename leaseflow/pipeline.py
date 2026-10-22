"""Dependency-free rental data pipeline. All supplied records are synthetic."""
from pathlib import Path
from datetime import datetime,timezone,date
import argparse,csv,hashlib,json,re,sqlite3,time,uuid
from contextlib import contextmanager

ROOT=Path(__file__).parent
CONTRACTS={
 'properties':{'key':'property_id','columns':['property_id','city','state','unit_count','updated_at']},
 'leases':{'key':'lease_id','columns':['lease_id','property_id','monthly_rent_cents','start_date','end_date','updated_at']},
 'payments':{'key':'payment_id','columns':['payment_id','lease_id','amount_cents','paid_at','updated_at']},
}
def now():return datetime.now(timezone.utc).isoformat(timespec='seconds')
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'))
def digest(value):return hashlib.sha256(canonical(value).encode()).hexdigest()
def connect(db):
 conn=sqlite3.connect(str(db));conn.row_factory=sqlite3.Row;conn.execute('PRAGMA foreign_keys=ON');return conn
@contextmanager
def session(db):
 conn=connect(db)
 try:
  with conn:yield conn
 finally:conn.close()
def initialize(conn):
 conn.executescript((ROOT/'schema.sql').read_text(encoding='utf-8'))
 # SQL view definitions contain no untrusted input; applied before the ingestion transaction.
 conn.executescript((ROOT/'marts.sql').read_text(encoding='utf-8'))
def timestamp(value):
 parsed=datetime.fromisoformat(value.replace('Z','+00:00'))
 if parsed.tzinfo is None:raise ValueError('Timezone required')
 return parsed.astimezone(timezone.utc).isoformat(timespec='microseconds')
def integer(value,minimum):
 if not re.fullmatch(r'\d+|-[0-9]+',str(value)):raise ValueError('Integer required')
 result=int(value)
 if result<minimum:raise ValueError('Outside range')
 return result
def validate(source,raw,conn):
 row={k:(v or '').strip() for k,v in raw.items()};errors=[]
 for field in CONTRACTS[source]['columns']:
  if not row.get(field):errors.append(('required',f'{field} is required.'))
 if errors:return row,errors
 key=CONTRACTS[source]['key']
 if not re.fullmatch(r'[A-Za-z0-9_-]{1,60}',row[key]):errors.append(('identifier',f'{key} has an invalid format.'))
 try:row['updated_at']=timestamp(row['updated_at'])
 except (ValueError,TypeError):errors.append(('timestamp','updated_at must be an ISO timestamp with a timezone.'))
 if source=='properties':
  try:row['unit_count']=integer(row['unit_count'],1)
  except ValueError:errors.append(('range','unit_count must be a positive integer.'))
  if not re.fullmatch(r'[A-Z]{2}',row['state']):errors.append(('state','state must use a two-letter uppercase code.'))
 elif source=='leases':
  try:row['monthly_rent_cents']=integer(row['monthly_rent_cents'],1)
  except ValueError:errors.append(('amount','monthly_rent_cents must be a positive integer.'))
  try:
   start=date.fromisoformat(row['start_date']);end=date.fromisoformat(row['end_date']);row['start_date']=start.isoformat();row['end_date']=end.isoformat()
   if end<start:raise ValueError('End before start')
  except ValueError:errors.append(('date_order','Lease dates must be ISO dates with end_date >= start_date.'))
  if not conn.execute('SELECT 1 FROM properties WHERE property_id=?',(row['property_id'],)).fetchone():errors.append(('foreign_key','property_id is not available in curated properties.'))
 else:
  try:row['amount_cents']=integer(row['amount_cents'],0)
  except ValueError:errors.append(('amount','amount_cents must be a non-negative integer.'))
  try:row['paid_at']=date.fromisoformat(row['paid_at']).isoformat()
  except ValueError:errors.append(('date','paid_at must be an ISO date.'))
  if not conn.execute('SELECT 1 FROM leases WHERE lease_id=?',(row['lease_id'],)).fetchone():errors.append(('foreign_key','lease_id is not available in curated leases.'))
 return row,errors
def read_batch(folder):
 batches={}
 for source,contract in CONTRACTS.items():
  with (Path(folder)/(source+'.csv')).open(encoding='utf-8-sig',newline='') as stream:
   reader=csv.DictReader(stream)
   if reader.fieldnames!=contract['columns']:raise ValueError(f'Schema drift in {source}: expected exact columns {contract["columns"]}.')
   rows=list(reader)
   if any(None in row or any(v is None for v in row.values()) for row in rows):raise ValueError(f'Malformed CSV row in {source}.')
   batches[source]=rows
 return batches
def issue(conn,run_id,source,entity_id,raw,rule,message,severity='error'):
 issue_id=digest({'source':source,'raw':raw,'rule':rule})[:20]
 conn.execute('''INSERT INTO issues VALUES(?,?,?,?,?,?,?,?,?,1)
 ON CONFLICT(issue_id) DO UPDATE SET last_seen_run=excluded.last_seen_run,active=1''',
 (issue_id,source,entity_id,rule,severity,message,canonical(raw),run_id,run_id))
def ingest(folder,db):
 db=Path(db);db.parent.mkdir(parents=True,exist_ok=True);conn=connect(db);initialize(conn)
 run_id=uuid.uuid4().hex;started=time.perf_counter()
 conn.execute('INSERT INTO runs(run_id,started_at,status) VALUES(?,?,?)',(run_id,now(),'running'));conn.commit()
 counts={'read':0,'inserted':0,'updated':0,'unchanged':0,'stale':0,'duplicate':0,'quarantined':0}
 try:
  batches=read_batch(folder)
  with conn:
   conn.execute('UPDATE issues SET active=0')
   for source,rows in batches.items():
    contract=CONTRACTS[source];key=contract['key'];seen=set()
    for line_number,raw in enumerate(rows,start=2):
     counts['read']+=1;row_hash=digest(raw);entity=raw.get(key,'').strip()
     conn.execute('INSERT OR IGNORE INTO bronze_records VALUES(?,?,?,?)',(source,row_hash,canonical(raw),run_id))
     row,errors=validate(source,raw,conn)
     if errors:
      outcome='quarantined'
      for rule,message in errors:issue(conn,run_id,source,entity,raw,rule,message)
     elif row_hash in seen:
      outcome='duplicate';issue(conn,run_id,source,entity,raw,'duplicate','Repeated identical row in this batch; retained once.','warning')
     else:
      seen.add(row_hash)
      old=conn.execute(f'SELECT * FROM {source} WHERE {key}=?',(row[key],)).fetchone()
      if old and row['updated_at']<old['updated_at']:outcome='stale'
      elif old and row['updated_at']==old['updated_at']:
       if any(row[c]!=old[c] for c in contract['columns']):
        outcome='quarantined';issue(conn,run_id,source,entity,raw,'version_conflict','Same business key and version contain conflicting values; no overwrite.')
       else:outcome='unchanged'
      else:
       outcome='updated' if old else 'inserted';columns=contract['columns']
       assignments=','.join(f'{c}=excluded.{c}' for c in columns if c!=key)
       conn.execute(f'INSERT INTO {source} ({",".join(columns)}) VALUES({",".join("?" for _ in columns)}) ON CONFLICT({key}) DO UPDATE SET {assignments}',tuple(row[c] for c in columns))
      if outcome!='quarantined':conn.execute('''INSERT INTO watermarks VALUES(?,?) ON CONFLICT(source) DO UPDATE SET max_accepted_updated_at=MAX(max_accepted_updated_at,excluded.max_accepted_updated_at)''',(source,row['updated_at']))
     counts[outcome]+=1
     conn.execute('INSERT INTO row_outcomes VALUES(?,?,?,?,?,?)',(run_id,source,line_number,entity,outcome,row_hash))
   counts['elapsed_ms']=round((time.perf_counter()-started)*1000,2)
   conn.execute('UPDATE runs SET finished_at=?,status=?,metrics_json=? WHERE run_id=?',(now(),'success',canonical(counts),run_id))
 except Exception as error:
  conn.rollback();conn.execute('UPDATE runs SET finished_at=?,status=?,error=? WHERE run_id=?',(now(),'failed',str(error),run_id));conn.commit();raise
 finally:conn.close()
 return {'run_id':run_id,**counts}
def snapshot(db):
 conn=connect(db)
 def query(sql,params=()):return [dict(row) for row in conn.execute(sql,params)]
 result={'generated_at':now(),'data_scope':'Synthetic fixture records only. No real renter data or underwriting decisions.',
 'counts':{table:conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0] for table in ['properties','leases','payments','bronze_records']},
 'runs':query('SELECT * FROM runs ORDER BY rowid DESC LIMIT 12'),'issues':query('SELECT * FROM issues WHERE active=1 ORDER BY severity,source,rule'),
 'source_outcomes':query('SELECT source,outcome,COUNT(*) AS count FROM row_outcomes WHERE run_id=(SELECT run_id FROM runs WHERE status="success" ORDER BY rowid DESC LIMIT 1) GROUP BY source,outcome'),
 'property_summary':query('SELECT * FROM mart_property_summary ORDER BY property_id'),
 'property_day':query('SELECT * FROM mart_property_day ORDER BY activity_date,property_id'),
 'watermarks':query('SELECT * FROM watermarks ORDER BY source')}
 for run in result['runs']:run['metrics']=json.loads(run.pop('metrics_json') or '{}')
 conn.close();return result
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--input',type=Path,default=ROOT/'fixtures');parser.add_argument('--db',type=Path,default=ROOT/'var'/'warehouse.db');parser.add_argument('--export',type=Path)
 args=parser.parse_args();result=ingest(args.input,args.db);print(json.dumps(result,indent=2))
 if args.export:args.export.parent.mkdir(parents=True,exist_ok=True);args.export.write_text(json.dumps(snapshot(args.db),indent=2),encoding='utf-8')
if __name__=='__main__':main()
