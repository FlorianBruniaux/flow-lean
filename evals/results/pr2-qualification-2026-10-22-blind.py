"""Blind paired responses: seeded A/B labels per case, key written separately."""
import json
import random
import sys
from pathlib import Path

plan = Path(sys.argv[1])
out = Path(sys.argv[2])
cases = {c["id"]: c for c in map(json.loads, (plan / "cases.jsonl").read_text(encoding="utf-8").splitlines())}
rows = [json.loads(l) for l in (plan / "responses.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
by_case = {}
for r in rows:
    by_case.setdefault(r["case_id"], {})[r["condition"]] = r["response"]
rng = random.Random(20261022)
blind, key = [], {}
for cid in sorted(by_case):
    pair = by_case[cid]
    assert set(pair) == {"comparator", "candidate"}, (cid, sorted(pair))
    order = ["comparator", "candidate"]
    rng.shuffle(order)
    key[cid] = {"A": order[0], "B": order[1]}
    c = cases[cid]
    blind.append({"case_id": cid, "category": c["category"], "risk": c["risk"], "prompt": c["prompt"],
                  "criteria": c["criteria"], "A": pair[order[0]], "B": pair[order[1]]})
(out / "pr2-blind.jsonl").write_text("".join(json.dumps(b, ensure_ascii=False) + "\n" for b in blind), encoding="utf-8")
(out / "pr2-blind-key.json").write_text(json.dumps({"seed": 20261022, "key": key}, indent=2), encoding="utf-8")
print(len(blind), "cases blinded")
