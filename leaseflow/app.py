"""Loopback-only data app: inspect warehouse results and CRUD issue notes."""
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse
import argparse,json,re
from pipeline import ROOT,connect,session,snapshot,now

def make_handler(db,web=None):
 web=Path(web or ROOT).resolve()
 class Handler(BaseHTTPRequestHandler):
  def log_message(self,*args):pass
  def send_json(self,status,value):
   body=json.dumps(value).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(body)
  def do_GET(self):
   route=urlparse(self.path).path
   if route=='/api/overview':return self.send_json(200,snapshot(db))
   if route=='/api/notes':
    with session(db) as conn:rows=[dict(r) for r in conn.execute('SELECT * FROM notes ORDER BY note_id')]
    return self.send_json(200,rows)
   if route.startswith('/api/'):return self.send_json(404,{'error':'Not found'})
   file=(web/('index.html' if route=='/' else route.lstrip('/'))).resolve()
   if not file.is_relative_to(web) or not file.is_file() or file.suffix not in {'.html','.css','.js','.json','.md','.py','.sql','.csv'}:return self.send_json(404,{'error':'Not found'})
   content=file.read_bytes();self.send_response(200);self.send_header('Content-Type',{'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json'}.get(file.suffix,'text/plain; charset=utf-8'));self.end_headers();self.wfile.write(content)
  def mutate(self,method):
   origin=self.headers.get('Origin')
   if origin and origin not in [f'http://127.0.0.1:{self.server.server_port}',f'http://localhost:{self.server.server_port}']:return self.send_json(403,{'error':'Origin rejected'})
   route=urlparse(self.path).path
   if route!='/api/notes' and not re.fullmatch(r'/api/notes/\d+',route):return self.send_json(404,{'error':'Not found'})
   length=int(self.headers.get('Content-Length','0'))
   if length<0 or length>4096:return self.send_json(413,{'error':'Body too large'})
   try:body=json.loads(self.rfile.read(length) or b'{}')
   except (ValueError,TypeError):return self.send_json(400,{'error':'Invalid JSON'})
   if not isinstance(body,dict):return self.send_json(400,{'error':'Expected an object'})
   text=body.get('text','')
   if method!='DELETE' and (not isinstance(text,str) or not 1<=len(text.strip())<=1000):return self.send_json(400,{'error':'Note must contain 1-1000 characters'})
   with session(db) as conn:
    if method=='POST':
     issue_id=body.get('issue_id')
     if not isinstance(issue_id,str) or not conn.execute('SELECT 1 FROM issues WHERE issue_id=?',(issue_id,)).fetchone():return self.send_json(400,{'error':'Unknown issue'})
     cursor=conn.execute('INSERT INTO notes(issue_id,text,created_at,updated_at) VALUES(?,?,?,?)',(issue_id,text.strip(),now(),now()));note_id=cursor.lastrowid
    else:
     if route=='/api/notes':return self.send_json(400,{'error':'A note ID is required'})
     note_id=int(route.rsplit('/',1)[1])
     if not conn.execute('SELECT 1 FROM notes WHERE note_id=?',(note_id,)).fetchone():return self.send_json(404,{'error':'Unknown note'})
     if method=='DELETE':conn.execute('DELETE FROM notes WHERE note_id=?',(note_id,));conn.commit();return self.send_json(200,{'deleted':note_id})
     conn.execute('UPDATE notes SET text=?,updated_at=? WHERE note_id=?',(text.strip(),now(),note_id))
    note=dict(conn.execute('SELECT * FROM notes WHERE note_id=?',(note_id,)).fetchone())
   self.send_json(201 if method=='POST' else 200,note)
  def do_POST(self):self.mutate('POST')
  def do_PATCH(self):self.mutate('PATCH')
  def do_DELETE(self):self.mutate('DELETE')
 return Handler
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--db',type=Path,default=ROOT/'var'/'warehouse.db');parser.add_argument('--port',type=int,default=4180);args=parser.parse_args()
 if not args.db.is_file():parser.error('Run the pipeline first to create a warehouse.')
 server=ThreadingHTTPServer(('127.0.0.1',args.port),make_handler(args.db));print(f'LeaseFlow local data app: http://127.0.0.1:{args.port}',flush=True);server.serve_forever()
if __name__=='__main__':main()
