"""A preview must copy metadata, never replace the installed homonym."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which('node'),'Node is required for router fixture checks')
class RoutingPreviewTests(unittest.TestCase):
    def test_preview_replaces_only_copied_skill_and_preserves_live_catalog(self):
        with tempfile.TemporaryDirectory() as tmp:
            js=r'''
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {copyPreviewCatalog}=require(process.argv[1]);
assert.equal(typeof copyPreviewCatalog,'function','Missing non-mutating catalog preview');
const root=process.argv[2],live=path.join(root,'live'),candidate=path.join(root,'candidate');
for(const name of ['flow-lean','neighbor']) {
 const dir=path.join(live,name);fs.mkdirSync(path.join(dir,'evals'),{recursive:true});
 fs.writeFileSync(path.join(dir,'SKILL.md'),'original '+name);
 fs.writeFileSync(path.join(dir,'evals/scenarios.json'),JSON.stringify({skill:name}));
}
fs.mkdirSync(path.join(candidate,'evals'),{recursive:true});
fs.writeFileSync(path.join(candidate,'SKILL.md'),'candidate');
fs.writeFileSync(path.join(candidate,'evals/scenarios.json'),'candidate corpus');
const skills=['flow-lean','neighbor'].map(name=>({name,directory:path.join(live,name),skillMd:path.join(live,name,'SKILL.md')}));
for(const host of ['claude','codex']) {
 const home=path.join(root,host),report=copyPreviewCatalog(home,host,skills,candidate);
 assert.equal(report.source_skills,2);assert.equal(report.mirrored_skills,2);
 const dest=path.join(home,host==='claude'?'.claude':'.agents','skills');
 assert.equal(fs.readFileSync(path.join(dest,'flow-lean/SKILL.md'),'utf8'),'candidate');
 assert.equal(fs.readFileSync(path.join(dest,'flow-lean/evals/scenarios.json'),'utf8'),'candidate corpus');
 assert.equal(fs.readFileSync(path.join(dest,'neighbor/SKILL.md'),'utf8'),'original neighbor');
 assert.equal(fs.readFileSync(path.join(dest,'neighbor/evals/scenarios.json'),'utf8'),JSON.stringify({skill:'neighbor'}));
 assert.throws(()=>copyPreviewCatalog(home,host,skills,candidate));
}
assert.equal(fs.readFileSync(path.join(live,'flow-lean/SKILL.md'),'utf8'),'original flow-lean');
assert.equal(fs.readFileSync(path.join(live,'flow-lean/evals/scenarios.json'),'utf8'),JSON.stringify({skill:'flow-lean'}));
assert.throws(()=>copyPreviewCatalog(path.join(root,'bad'),'claude',[{name:'../escape'}],candidate));
'''
            result=subprocess.run(['node','-e',js,str(ROOT/'scripts/check_routing.cjs'),tmp],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)


if __name__=='__main__':unittest.main()
