#!/usr/bin/env python3
"""
rollback.py - Reverse a local update:
  - restores config.md from backup to its pre-install checksum
  - removes cache/new.json and its cache dir, created by the install
  - refuses to touch either file if it no longer matches the checksum
    recorded right after installation (concurrent writer detected)
  - writes a verification record to an external location, never inside
    the directories this script may remove

Prerequisite: any other process that edits root/config.md or
root/cache/new.json must take an exclusive flock() on
<root>/.rollback.lock before writing, and release it after. Without
that convention honored by the other writer, exclusion cannot be
guaranteed and this script will refuse to proceed safely.

Dependencies: Python 3.8+, POSIX fcntl (Linux/macOS only).
"""
import argparse
import fcntl
import hashlib
import json
import os
import shutil
import sys
import time


def sha256_of(path):
    if not os.path.isfile(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_record(verification_dir, record):
    os.makedirs(verification_dir, exist_ok=True)
    path = os.path.join(verification_dir, "rollback-record.jsonl")
    with open(path, "a") as f:
        f.write(json.dumps(record) + "\n")
    return path


def fail(verification_dir, reason, details):
    record = {
        "ts": time.time(),
        "result": "stopped",
        "reason": reason,
        "details": details,
    }
    rec_path = write_record(verification_dir, record)
    print(f"STOPPED: {reason}", file=sys.stderr)
    print(f"Verification record: {rec_path}", file=sys.stderr)
    sys.exit(2)


def main():
    p = argparse.ArgumentParser(description="Roll back config.md + cache/new.json install.")
    p.add_argument("--root", required=True, help="Root path of the update.")
    p.add_argument("--verification-dir", required=True,
                    help="External location (outside --root) for verification records.")
    p.add_argument("--config-backup", required=True,
                    help="Path to the original config.md backup to restore.")
    p.add_argument("--config-orig-checksum", required=True,
                    help="sha256 of config.md before install (expected after restore).")
    p.add_argument("--config-installed-checksum", required=True,
                    help="sha256 of config.md immediately after install (last known state).")
    p.add_argument("--new-json-installed-checksum", required=True,
                    help="sha256 of cache/new.json immediately after install.")
    args = p.parse_args()

    root = os.path.abspath(args.root)
    verification_dir = os.path.abspath(args.verification_dir)
    if verification_dir == root or verification_dir.startswith(root + os.sep):
        fail(verification_dir, "bad_config",
             "verification-dir must be outside root; it would be deleted by rollback")

    config_path = os.path.join(root, "config.md")
    cache_dir = os.path.join(root, "cache")
    new_json_path = os.path.join(cache_dir, "new.json")
    lock_path = os.path.join(root, ".rollback.lock")

    os.makedirs(root, exist_ok=True)
    lock_fd = open(lock_path, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        fail(verification_dir, "lock_held",
             "Another writer holds the lock. Stop for manual reconciliation; "
             "do not proceed, a hash check followed by a write is not atomic.")

    try:
        # Compare each target to the last state written by the install run,
        # under the lock, so no writer can race between check and write.
        cur_config_sum = sha256_of(config_path)
        cur_new_json_sum = sha256_of(new_json_path)

        if cur_config_sum != args.config_installed_checksum:
            fail(verification_dir, "concurrent_change_config",
                 {"expected": args.config_installed_checksum, "found": cur_config_sum})

        if os.path.isfile(new_json_path) and cur_new_json_sum != args.new_json_installed_checksum:
            fail(verification_dir, "concurrent_change_new_json",
                 {"expected": args.new_json_installed_checksum, "found": cur_new_json_sum})

        # Restore config.md from backup.
        shutil.copy2(args.config_backup, config_path)
        restored_sum = sha256_of(config_path)
        if restored_sum != args.config_orig_checksum:
            fail(verification_dir, "restore_checksum_mismatch",
                 {"expected": args.config_orig_checksum, "found": restored_sum})

        # Remove cache/new.json, created by install and absent before it.
        removed_new_json = False
        if os.path.isfile(new_json_path):
            os.remove(new_json_path)
            removed_new_json = True

        # Remove the cache dir only if now empty.
        removed_cache_dir = False
        if os.path.isdir(cache_dir) and not os.listdir(cache_dir):
            os.rmdir(cache_dir)
            removed_cache_dir = True

        record = {
            "ts": time.time(),
            "result": "rolled_back",
            "config_restored_checksum": restored_sum,
            "removed_new_json": removed_new_json,
            "removed_cache_dir": removed_cache_dir,
        }
        rec_path = write_record(verification_dir, record)
        print("Rollback complete.")
        print(f"Verification record: {rec_path}")
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()


if __name__ == "__main__":
    main()
