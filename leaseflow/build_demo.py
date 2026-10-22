"""Create an isolated, reproducible public snapshot from fixture runs."""
from pathlib import Path
import json,tempfile
from pipeline import ROOT,ingest,snapshot

with tempfile.TemporaryDirectory() as temp:
 db=Path(temp)/'demo.db'
 first=ingest(ROOT/'fixtures',db)
 second=ingest(ROOT/'fixtures',db)
 result=snapshot(db)
 result['demonstration']={'first_run':first,'repeat_run':second,'note':'Observed on the checked-in synthetic fixtures. Not a production workload or business outcome.'}
 (ROOT/'snapshot.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 print(json.dumps({'first_run':first,'repeat_run':second,'curated_rows':result['counts'],'active_issues':len(result['issues'])},indent=2))
