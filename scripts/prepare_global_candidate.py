#!/usr/bin/env python3
"""Prepare an inert, dual-host Flow Lean candidate. Never installs or calls a model."""
import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def prepare(config, output, routing_corpus=None):
    config, output = config.resolve(), output.resolve()
    if output.exists():
        raise ValueError("Use a fresh output directory; preserve earlier candidates")
    baseline = (config / "current").resolve()
    manifest = json.loads((baseline / "artifact-manifest.json").read_text())
    # Verify every manifested byte before constructing an inert source copy.
    for relative, expected in manifest["artifacts"].items():
        path = baseline / relative
        if expected["type"] == "symlink":
            assert path.is_symlink() and os.readlink(path) == expected["linkTarget"], relative
        else:
            assert not path.is_symlink() and path.is_file(), relative
            assert sha(path) == expected["hash"] and path.stat().st_mode & 0o777 == expected["mode"], relative
    extras = sorted(str(p.relative_to(baseline)) for p in baseline.rglob("*")
                    if (p.is_symlink() or p.is_file())
                    and str(p.relative_to(baseline)) not in manifest["artifacts"]
                    and p.name != "artifact-manifest.json")
    output.mkdir(parents=True)
    source = output / "source"
    source.mkdir()
    for name, expected in manifest["sources"].items():
        if isinstance(expected, dict):
            for relative, entry in expected.items():
                old = baseline / name / relative
                new = source / name / relative
                new.parent.mkdir(parents=True, exist_ok=True)
                if entry["type"] == "symlink":
                    assert os.readlink(old) == entry["linkTarget"]
                    new.symlink_to(entry["linkTarget"])
                else:
                    assert sha(old) == entry["hash"], str(old)
                    shutil.copy2(old, new)
        else:
            old = config / "src" / name
            assert sha(old) == expected, f"Baseline source drift: {name}"
            shutil.copy2(old, source / name)
    spec = json.loads((ROOT / "evals/candidates/v3.1-groups.json").read_text())
    rendered = "\n\n".join([spec["base"], *(g["text"] for g in spec["groups"])]) + "\n"
    assert rendered == (ROOT / "evals/candidates/minimal-v3.1.md").read_text()
    groups = {g["id"]: g["text"] for g in spec["groups"]}
    guardrails = "\n\n".join(groups[name] for name in ("fidelity", "evidence", "duration", "rollback")) + "\n\n"
    runtime = "Match the declared runtime version. Exercise argument-error and cleanup paths on that runtime before claiming compatibility.\n\n"
    skill_path = source / "skills/common/flow-lean/SKILL.md"
    skill = skill_path.read_text()
    start = skill.index("For an executable plan with a rollback,")
    end = skill.index("### Status report", start)
    skill = skill[:start] + guardrails + runtime + skill[end:]
    skill_path.write_text(skill)
    style_path = source / "claude-output-style.md"
    style = style_path.read_text()
    start = style.index("For an executable plan with a rollback,")
    end = style.index("Speak as the assistant.", start)
    style_path.write_text(style[:start] + guardrails + runtime + style[end:])
    if routing_corpus:
        routing = json.loads(routing_corpus.read_text())
        if routing.get("skill") != "flow-lean" or len(routing.get("positive", [])) < 8 or len(routing.get("negative", [])) < 2:
            raise ValueError("Invalid Flow Lean routing corpus")
        shutil.copy2(routing_corpus, source / "skills/common/flow-lean/evals/scenarios.json")
    catalog_path = source / "skills/catalog-manifest.json"
    catalog = json.loads(catalog_path.read_text())
    next(e for e in catalog["skills"]["common"] if e["name"] == "flow-lean")["sourceHash"] = sha(skill_path)
    catalog_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n")
    # Canonical-source patches preserve unrelated pending catalog entries.
    owned = ["skills/common/flow-lean/SKILL.md", "claude-output-style.md", "skills/catalog-manifest.json"]
    if routing_corpus:
        owned.append("skills/common/flow-lean/evals/scenarios.json")
    inventory, patches = [], []
    for relative in owned:
        live = config / "src" / relative
        before = live.read_text()
        if relative == "skills/catalog-manifest.json":
            current = json.loads(before)
            next(e for e in current["skills"]["common"] if e["name"] == "flow-lean")["sourceHash"] = sha(skill_path)
            after = json.dumps(current, indent=2, ensure_ascii=False) + "\n"
        else:
            # A changed live skill must not be silently replaced by the baseline.
            expected_path = baseline / (relative if relative.startswith("skills/") else "claude/output-styles/flow-lean.md")
            assert live.read_bytes() == expected_path.read_bytes(), f"Live source drift: {relative}"
            after = (source / relative).read_text()
        target = output / "canonical-source-candidate" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(after)
        inventory.append({"target": str(live), "preimage_sha256": sha(live), "candidate": str(target), "postimage_sha256": sha(target)})
        patches.extend(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile=str(live), tofile=str(target)))
    (output / "canonical-source.diff").write_text("".join(patches))
    result = subprocess.run(["node", str(config / "scripts/render.mjs"), "--source", str(source),
                             "--hooks", str(baseline / "hooks"), "--output", str(output / "releases"),
                             "--source-commit", manifest["sourceCommit"]], check=True, capture_output=True, text=True)
    release = json.loads(result.stdout)
    proof = {"status": "PREPARED_NOT_INSTALLED", "provider_calls": 0, "baseline_release": str(baseline),
             "baseline_manifest_sha256": sha(baseline / "artifact-manifest.json"),
             "unmanifested_baseline_files": extras, "source_updates": inventory,
             "release": release, "source": str(source),
             "integration": "Corrected v3.1 guardrails in full global skill and output style; legacy format/footer controls retained. Not the minimal comparison prompt.",
             "quality": "No new model comparison; prompt adherence and savings unverified."}
    encoded = json.dumps(proof, sort_keys=True, separators=(",", ":"))
    proof["review_digest"] = hashlib.sha256(encoded.encode()).hexdigest()
    (output / "preparation.json").write_text(json.dumps(proof, indent=2) + "\n")
    print(json.dumps({"status": proof["status"], "release": release, "baseline_extras": len(extras), "review_digest": proof["review_digest"]}))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--routing-corpus", type=Path)
    args = parser.parse_args()
    prepare(args.config, args.output, args.routing_corpus)
