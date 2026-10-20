"""Controlled test double with deliberate mutants. NOT a production rollback."""
import hashlib
from pathlib import Path
import shutil
import sys
import os

root, records, backup = map(Path, sys.argv[1:4])
original_hash, config_hash, cache_hash, mutant = sys.argv[4:8]
lock = root / ".lock"
config, new = root / "config.md", root / "cache/new.json"
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
try:
    if mutant == "file_lock":
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)
    else: lock.mkdir()
except FileExistsError:
    if mutant == "remove_other_lock": lock.rmdir()
    sys.exit(4)
try:
    if not backup.is_file() or digest(backup) != original_hash:
        sys.exit(5)
    if (config.is_symlink() or new.is_symlink() or digest(config) != config_hash
            or (digest(new) != cache_hash and not (mutant == "accept_missing" and not new.exists()))):
        if mutant == "partial_mutation":
            if new.exists(): new.unlink()
            shutil.copy2(backup, config)
        sys.exit(6)
    if mutant != "noop":
        if mutant == "overwrite_temp":
            temp = root / "config.md.rollback.tmp"
            shutil.copy2(backup, temp); temp.replace(config)
        else:
            shutil.copy2(backup, config)
        if mutant == "wrong_mode": config.chmod(0o600)
        if new.exists(): new.unlink()
        if not any((root / "cache").iterdir()): (root / "cache").rmdir()
        elif mutant == "delete_nonempty": shutil.rmtree(root / "cache")
    (records / "result.log").write_text("" if mutant == "empty_evidence" else "restored\n")
    if mutant == "tamper_evidence": (records / "prior-evidence.txt").unlink()
finally:
    if mutant == "leak_lock": (lock / "owner.pid").write_text("fixture\n")
    elif mutant == "file_lock": lock.unlink()
    else: lock.rmdir()
if mutant == "reported_retained_directory" and (root / "cache").exists(): sys.exit(6)
