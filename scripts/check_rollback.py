#!/usr/bin/env python3
"""Execute a reviewed rollback command against disposable fixtures, without a provider.

This is a behavior checker, NOT a sandbox for untrusted generated programs.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile

SCENARIOS = (
    "normal", "config_conflict", "cache_conflict", "missing_target",
    "unrelated_temp", "held_lock", "nonempty_cache", "invalid_backup", "missing_backup",
    "missing_config", "config_symlink", "cache_symlink",
)
REFUSALS = {"config_conflict", "cache_conflict", "missing_target", "held_lock",
            "invalid_backup", "missing_backup", "missing_config", "config_symlink", "cache_symlink"}
ORIGINAL = b"original\n"
INSTALLED = b"installed\n"
CACHE = b'{"installed":true}\n'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def snapshot(path):
    """Do not follow symlinks when observing the fixture after execution."""
    if path.is_symlink():
        return {"symlink": os.readlink(path)}
    if not path.exists():
        return None
    mode = stat.S_IMODE(path.stat().st_mode) if os.name != "nt" else None
    if path.is_file():
        return {"sha256": digest(path.read_bytes()), "mode": mode}
    return {"directory": True, "mode": mode}


def inside(base, value):
    path = Path(value)
    if not path.is_absolute():
        path = base / path
    if not path.resolve().is_relative_to(base.resolve()):
        raise ValueError("Adapter lock must stay inside the disposable fixture")
    return path


def check(adapter, scenarios=SCENARIOS):
    sources = adapter.get("source_files", [])
    if not sources or any(not Path(p).is_file() for p in sources):
        raise ValueError("source_files must list the reviewed executable source files")
    source_hashes = {str(Path(p).resolve()): digest(Path(p).read_bytes()) for p in sources}
    if adapter.get("lock_kind") not in {"directory", "flock", "exclusive_file"}:
        raise ValueError("lock_kind must be directory, flock or exclusive_file")
    success_codes = adapter.get("success_codes", {})
    if (not isinstance(success_codes, dict) or not set(success_codes) <= set(SCENARIOS) - REFUSALS
            or any(not isinstance(v, list) or not v or any(type(n) is not int for n in v)
                   for v in success_codes.values())):
        raise ValueError("success_codes must declare integer exit codes for success scenarios only")
    if not isinstance(adapter.get("command"), list) or not adapter["command"]:
        raise ValueError("command must be a nonempty argv list")
    if not set(scenarios) <= set(SCENARIOS):
        raise ValueError("Unknown rollback scenario")
    timeout = adapter.get("timeout_seconds", 10)
    if not isinstance(timeout, (int, float)) or not 0 < timeout <= 60:
        raise ValueError("timeout_seconds must be between 0 and 60")
    results = []
    for scenario in scenarios:
        if adapter["lock_kind"] == "flock" and os.name != "posix":
            results.append({"scenario": scenario, "status": "UNKNOWN",
                            "reason": "flock probes require POSIX"})
            continue
        with tempfile.TemporaryDirectory(prefix="flow-lean-rollback-") as tmp:
            base = Path(tmp)
            root, records, backup = base / "root", base / "records", base / "original.md"
            root.mkdir(); records.mkdir(); (root / "cache").mkdir()
            config, new = root / "config.md", root / "cache/new.json"
            config.write_bytes(INSTALLED); new.write_bytes(CACHE); backup.write_bytes(ORIGINAL)
            backup.chmod(0o640); config.chmod(0o600)
            old_record = records / "prior-evidence.txt"
            old_record.write_text("Prior verification must survive.\n", encoding="utf-8")
            extra = root / "cache/unrelated.txt"
            marker = root / "config.md.rollback.tmp"
            if scenario == "config_conflict": config.write_bytes(b"concurrent config\n")
            if scenario == "cache_conflict": new.write_bytes(b"concurrent cache\n")
            if scenario == "missing_target": new.unlink()
            if scenario == "missing_config": config.unlink()
            if scenario in {"config_symlink", "cache_symlink"}:
                target = config if scenario == "config_symlink" else new
                extra.write_bytes(target.read_bytes())
                target.unlink()
                target.symlink_to(extra)
            if scenario == "unrelated_temp": marker.write_bytes(b"unrelated work\n")
            if scenario == "nonempty_cache": extra.write_bytes(b"unrelated cache\n")
            if scenario == "invalid_backup": backup.write_bytes(b"invalid backup\n")
            if scenario == "missing_backup": backup.unlink()
            values = {"root": str(root), "records": str(records), "backup": str(backup),
                      "original_sha256": digest(ORIGINAL), "config_sha256": digest(INSTALLED),
                      "cache_sha256": digest(CACHE)}
            lock = inside(base, adapter["lock_path"].format_map(values))
            lock.parent.mkdir(parents=True, exist_ok=True)
            held = None
            if scenario == "held_lock":
                if adapter["lock_kind"] == "directory":
                    lock.mkdir()
                elif adapter["lock_kind"] == "exclusive_file":
                    lock.write_text(adapter.get("held_lock_text", "external owner\n"), encoding="utf-8")
                else:
                    import fcntl
                    held = lock.open("w")
                    fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
            lock_inode = lock.stat().st_ino if lock.exists() else None
            held_lock_state = snapshot(lock)
            watched = (config, new, root / "cache", marker, extra, backup, old_record)
            before = [snapshot(path) for path in watched]
            command = [part.format_map(values) for part in adapter["command"]]
            stdout = stderr = ""
            code = None
            error = None
            try:
                run = subprocess.run(command, cwd=base, capture_output=True, text=True,
                                     encoding="utf-8", errors="replace", timeout=timeout)
                code, stdout, stderr = run.returncode, run.stdout, run.stderr
            except (OSError, subprocess.TimeoutExpired) as exc:
                error = str(exc)
            finally:
                if held is not None:
                    held.close()
            after = [snapshot(path) for path in watched]
            checks = {"command_completed": error is None,
                      "backup_preserved": after[5] == before[5],
                      "prior_evidence_preserved": after[6] == before[6],
                      "unrelated_paths_preserved": after[3:5] == before[3:5]}
            if scenario in REFUSALS:
                checks["refuses_before_mutation"] = code is not None and code != 0 and after[:3] == before[:3]
            else:
                checks["restores_original_content"] = (
                    code in success_codes.get(scenario, [0]) and after[0] is not None
                    and after[0].get("sha256") == digest(ORIGINAL))
                checks["removes_created_file"] = after[1] is None
                checks["removes_only_empty_created_directory"] = (
                    (root / "cache").is_dir() if scenario == "nonempty_cache" else after[2] is None)
                if os.name != "nt":
                    checks["restores_original_mode"] = after[0] is not None and after[0].get("mode") == 0o640
                logs = [p for p in records.rglob("*") if p.is_file() and not p.is_symlink()
                        and p not in (old_record, lock) and p.stat().st_size > 0]
                checks["new_nonempty_evidence_retained"] = bool(logs)
            if scenario == "held_lock":
                checks["preserves_other_owners_lock"] = (
                    lock.exists() and lock.stat().st_ino == lock_inode and snapshot(lock) == held_lock_state)
            elif adapter["lock_kind"] in {"directory", "exclusive_file"}:
                checks["releases_owned_lock"] = not lock.exists()
            else:
                import fcntl
                # A persistent flock support file is not itself a leaked lock.
                try:
                    with lock.open("a") as stream:
                        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    checks["releases_owned_lock"] = True
                except OSError:
                    checks["releases_owned_lock"] = False
            results.append({"scenario": scenario, "status": "PASS" if all(checks.values()) else "FAIL",
                            "checks": checks, "before": before, "after": after, "returncode": code,
                            "stdout": stdout, "stderr": stderr, "error": error})
    status = "FAIL" if any(r["status"] == "FAIL" for r in results) else (
        "UNKNOWN" if not results or any(r["status"] == "UNKNOWN" for r in results) else "PASS")
    after_hashes = {p: digest(Path(p).read_bytes()) if Path(p).is_file() else None for p in source_hashes}
    if after_hashes != source_hashes: status = "FAIL"
    return {"status": status, "scope": "Disposable fixture behavior; not a sandbox or proof of race safety",
            "source_hashes": source_hashes, "source_hashes_after": after_hashes,
            "platform": os.name, "mode_checks": "UNKNOWN" if os.name == "nt" else "enabled",
            "results": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("adapter", type=Path)
    parser.add_argument("--reviewed", action="store_true", help="Confirm command code was inspected locally")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.reviewed:
        parser.error("Read the command code first; disposable directories are not isolation. Then use --reviewed.")
    if args.output.exists():
        parser.error("Use a new output path to preserve prior evidence")
    adapter_bytes = args.adapter.read_bytes()
    report = check(json.loads(adapter_bytes))
    report["adapter_sha256"] = digest(adapter_bytes)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"status": report["status"], "scenarios": len(report["results"])}))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
