"""Offline fault injection: unchanged generated code can return 3 after mutation."""
import contextlib, hashlib, importlib.util, io, json, os, sys, tempfile
from pathlib import Path
from unittest.mock import patch
PLAN=Path(__file__).resolve().parent
results=[]
for label in ('A','B'):
    source=PLAN/('rollback-'+label+'.py')
    spec=importlib.util.spec_from_file_location('rollback_probe_'+label,source)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory() as temp:
        base=Path(temp).resolve();root=base/'root';root.mkdir();(root/'cache').mkdir()
        config=root/'config.md';config.write_bytes(b'installed\n')
        new=root/'cache/new.json';new.write_bytes(b'created\n')
        backup=base/'backup';backup.write_bytes(b'original\n')
        records=base/'records';records.mkdir()
        args=[str(source),'--root',str(root),'--records',str(records),'--backup',str(backup),
              '--original-sha256',hashlib.sha256(backup.read_bytes()).hexdigest(),
              '--config-sha256',hashlib.sha256(config.read_bytes()).hexdigest(),
              '--cache-sha256',hashlib.sha256(new.read_bytes()).hexdigest(),'--writers-stopped']
        real_replace=module.os.replace
        def replace_then_change_lock(*args):
            real_replace(*args)
            (root/'.rollback.lock/owner.json').write_text('foreign owner')
        out,err=io.StringIO(),io.StringIO()
        with patch.object(sys,'argv',args),patch.object(module.os,'replace',side_effect=replace_then_change_lock),contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):
            code=module.main()
        events=[json.loads(line) for p in records.glob('rollback-*.jsonl') for line in p.read_text().splitlines()]
        result={'label':label,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                'exit_code':code,'stdout':out.getvalue(),'stderr':err.getvalue(),
                'before':{'config':'installed\n','cache_file_exists':True},
                'after':{'config':config.read_text(),'cache_file_exists':new.exists(),'lock_owner':(root/'.rollback.lock/owner.json').read_text()},
                'receipt_stages':[e['stage'] for e in events],
                'fault':'Injected lock-owner change after real os.replace; tests defensive error classification, not writer exclusion.'}
        assert code==3 and config.read_bytes()==b'original\n' and not new.exists()
        assert result['receipt_stages']==['validated','restored','verified','failed']
        results.append(result)
report={'runtime':sys.version,'results':results,'conclusion':'Exit 3 does not prove absence of target mutations. The script retains the foreign lock and records failure correctly.'}
(PLAN/'exit-contract-probe.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
