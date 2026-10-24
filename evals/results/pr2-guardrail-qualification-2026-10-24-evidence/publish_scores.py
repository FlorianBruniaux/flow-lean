"""Unmask already-frozen grades; regenerate the artifact inventory offline."""
import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent;PREFIX=P.parent/'pr2-guardrail-qualification-2026-10-24'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=json.loads((P/'grading-freeze.json').read_text())
assert sha(P/'grades-blind.jsonl')==f['sha256']
assert sha(P/'fact-audit-blind.json')==f['fact_audit_sha256']
assert sha(P/'actor-audit-blind.json')==f['actor_audit_sha256']
key=json.loads((P/'blind-key.json').read_text())['key']
g=[json.loads(l) for l in (P/'grades-blind.jsonl').read_text().splitlines()]
scores=[{**r,'condition':key[r['case_id']][r['label']]} for r in g]
Path(str(PREFIX)+'-scores.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in scores))
paths=[p for p in P.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='artifact-hashes.json']
paths += [Path(str(PREFIX)+s) for s in ('.jsonl','.jsonl.attempts.jsonl','.jsonl.manifest.json','-scores.jsonl')]
(P/'artifact-hashes.json').write_text(json.dumps({str(p.relative_to(P.parent)):sha(p) for p in sorted(paths)},indent=2)+'\n')
for r in scores:
 if r['blocker']:print(r['condition'],r['case_id'],r['label'])
