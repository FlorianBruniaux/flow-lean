"""Offline demonstration of why expected postimages must come from installation."""
import hashlib,json,subprocess,sys,tempfile
from pathlib import Path
PLAN=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
results=[]
for label in ('A','B'):
 source=PLAN/('rollback-'+label+'.py')
 for inputs in ('trusted_installation','recomputed_current'):
  with tempfile.TemporaryDirectory() as tmp:
   base=Path(tmp).resolve();root=base/'root';root.mkdir();cache=root/'cache';cache.mkdir();records=base/'records';records.mkdir()
   backup=base/'backup';backup.write_text('original\n');config=root/'config.md';config.write_text('installed\n');new=cache/'new.json';new.write_text('created\n')
   expected_config,expected_new=sha(config),sha(new)
   config.write_text('concurrent user edit\n');new.write_text('concurrent cache edit\n')
   before={'config':config.read_text(),'new':new.read_text()}
   if inputs=='recomputed_current':expected_config,expected_new=sha(config),sha(new)
   r=subprocess.run([sys.executable,'-I',str(source),'--root',str(root),'--records',str(records),'--backup',str(backup),'--original-sha256',sha(backup),'--config-sha256',expected_config,'--cache-sha256',expected_new,'--writers-stopped'],capture_output=True,text=True)
   after={'config':config.read_text(),'new':new.read_text() if new.exists() else None}
   events=[json.loads(line) for p in records.glob('*.jsonl') for line in p.read_text().splitlines()]
   assert (r.returncode==3 and before==after) if inputs=='trusted_installation' else (r.returncode==0 and after=={'config':'original\n','new':None})
   results.append({'label':label,'source_sha256':sha(source),'inputs':inputs,'before':before,'after':after,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'receipt_stages':[e['stage'] for e in events]})
report={'results':results,'conclusion':'Trusted installation checksums refuse pre-existing concurrent edits. Recomputing expected values from current targets authorizes their overwrite and deletion. All writers are stopped during both fixture runs; this is an input-provenance failure, not a lock race.'}
(PLAN/'postimage-input-probe.json').write_text(json.dumps(report,indent=2)+'\n')
print('4 input-provenance checks passed')
