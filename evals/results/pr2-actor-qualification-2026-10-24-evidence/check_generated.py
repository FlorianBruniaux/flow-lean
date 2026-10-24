"""Offline replay of fully reviewed scripts; never modifies a generated program."""
import contextlib, hashlib, importlib.util, io, json, re, sys, unittest
from pathlib import Path
plan=Path(__file__).resolve().parent
root=plan.parents[2]
sys.path.insert(0,str(root/'scripts'))
sys.path.insert(0,str(root/'tests'))
from check_rollback import check
import test_reference_rollback as suite
key=json.loads((plan/'blind-key.json').read_text())['key']['rollback-concurrent-edits']
answers={r['condition']:r['response'] for r in map(json.loads,(root/'evals/results/pr2-actor-qualification-2026-10-24.jsonl').read_text().splitlines()) if r['case_id']=='rollback-concurrent-edits'}
reference=(plan/'sources/skills/flow-lean/scripts/rollback_reference.py').read_bytes()
for label,arm in key.items():
 code=re.search(r'```python\n(.*?)```',answers[arm],re.S).group(1).encode()
 assert code==reference, 'Inspect changed source before execution'
 path=plan/('rollback-'+label+'.py')
 with path.open('xb') as f:f.write(code)
 spec=importlib.util.spec_from_file_location('generated_'+label,path)
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 suite.reference=module;suite.SOURCE=path
 adapter=suite.adapter();adapter['command'].insert(1,'-I')
 report=check(adapter)
 stream=io.StringIO()
 tests=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(suite.ReferenceRollbackTests),unittest.defaultTestLoader.loadTestsFromTestCase(suite.ReferencePortabilityTests)])
 result=unittest.TextTestRunner(stream=stream,verbosity=2).run(tests)
 report['supplemental_tests']={'count':result.testsRun,'success':result.wasSuccessful(),'log':stream.getvalue(),'source':'sources/tests/test_reference_rollback.py'}
 report['matches_supplied_reference']=True
 report['python']=sys.version
 report['argument_errors']=[]
 import subprocess
 for args in ([],['--root'],['--help'],['--bogus']):
  r=subprocess.run([sys.executable,'-I',str(path),*args],capture_output=True,text=True)
  report['argument_errors'].append({'args':args,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
 assert hashlib.sha256(path.read_bytes()).hexdigest()==hashlib.sha256(reference).hexdigest()
 (plan/('rollback-'+label+'-adapter.json')).write_text(json.dumps(adapter,indent=2)+'\n')
 (plan/('rollback-'+label+'-report.json')).write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'label':label,'scenarios_passed':sum(r['status']=='PASS' for r in report['results']),'supplemental_tests':result.testsRun,'supplemental_success':result.wasSuccessful(),'exact_reference_copy':True}))
