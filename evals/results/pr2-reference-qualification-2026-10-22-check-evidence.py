"""Offline positive and corruption tests for this campaign's receipt verifier."""
import copy, hashlib, importlib.util, json, shutil, tempfile
from pathlib import Path
BASE=Path(__file__).resolve().parent
NAME='pr2-reference-qualification-2026-10-22'
spec=importlib.util.spec_from_file_location('campaign_verifier',BASE/(NAME+'-verify.py'))
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
expected=json.loads((BASE/(NAME+'-summary.json')).read_text())
assert v.verify()==expected
results=[{'test':'published_summary_reproduced','status':'PASS'}]
for scenario in ('missing_answer','receipt_cost','condition_instructions','frozen_grade','supplemental_failure'):
 with tempfile.TemporaryDirectory() as temp:
  root=Path(temp)
  shutil.copytree(BASE/(NAME+'-evidence'),root/(NAME+'-evidence'),ignore=shutil.ignore_patterns('__pycache__'))
  for suffix in ('.jsonl','.jsonl.attempts.jsonl','.jsonl.manifest.json','-scores.jsonl'):
   shutil.copyfile(BASE/(NAME+suffix),root/(NAME+suffix))
  v.PREFIX=root/NAME;v.EVIDENCE=root/(NAME+'-evidence')
  if scenario=='missing_answer':
   target=root/(NAME+'.jsonl');lines=target.read_text().splitlines();target.write_text('\n'.join(lines[:-1])+'\n')
  elif scenario=='receipt_cost':
   target=root/(NAME+'.jsonl.attempts.jsonl');lines=list(map(json.loads,target.read_text().splitlines()));next(r for r in lines if r['event']=='finished')['cost_usd']=0;target.write_text(''.join(json.dumps(r)+'\n' for r in lines))
  elif scenario=='condition_instructions':
   target=root/(NAME+'.jsonl.manifest.json');data=json.loads(target.read_text());data['conditions']['candidate']['instructions']+=' altered';target.write_text(json.dumps(data))
  elif scenario=='frozen_grade':
   target=v.EVIDENCE/'grades-blind.jsonl';lines=list(map(json.loads,target.read_text().splitlines()));lines[0]['blocker']=False;target.write_text(''.join(json.dumps(r)+'\n' for r in lines))
  else:
   target=v.EVIDENCE/'rollback-A-report.json';data=json.loads(target.read_text());data['supplemental_tests']['success']=False;target.write_text(json.dumps(data))
  # Rehash only the corrupt artifact to exercise semantic checks beyond inventory.
  inventory=v.EVIDENCE/'artifact-hashes.json';data=json.loads(inventory.read_text());data[str(target.relative_to(root))]=hashlib.sha256(target.read_bytes()).hexdigest();inventory.write_text(json.dumps(data))
  try:v.verify()
  except ValueError as exc:results.append({'test':scenario,'status':'PASS','rejected_with':str(exc)})
  else:raise AssertionError('Corruption accepted: '+scenario)
print(json.dumps({'provider_calls':0,'tests':results},indent=2))
