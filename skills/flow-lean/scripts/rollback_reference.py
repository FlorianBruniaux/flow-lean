#!/usr/bin/env python3
"""Bounded rollback reference: Python 3.9+, POSIX, stdlib only.

Requires all writers stopped for the full operation. This cooperative lock does
not enforce that prerequisite. Not a transaction, crash-recovery system or
sandbox. Exit 3 (refusal) and exit 4 (I/O failure) do not identify the mutation
phase: either may occur before or after targets changed. Inspect receipts and
state before any retry. See ../references/rollback.md before using real files.
"""
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile


class Refusal(RuntimeError):
    """A prerequisite, verification or cleanup conflict; targets may have changed."""


def physical(path, directory=False):
    """Require absolute physical paths; never resolve away a substituted link."""
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts:
        raise Refusal('Use an absolute physical path without ..: ' + str(path))
    try:
        for item in [*reversed(path.parents), path]:
            mode = item.lstat().st_mode
            if stat.S_ISLNK(mode):
                raise Refusal('Symlink in path: ' + str(item))
            if item != path and not stat.S_ISDIR(mode):
                raise Refusal('Non-directory parent: ' + str(item))
        info = path.lstat()
    except FileNotFoundError as exc:
        raise Refusal('Missing expected path: ' + str(path)) from exc
    if directory:
        if not stat.S_ISDIR(info.st_mode):
            raise Refusal('Expected directory: ' + str(path))
    elif not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise Refusal('Expected a single-link regular file: ' + str(path))
    return path


def image(path):
    info = path.stat()
    return {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'mode': stat.S_IMODE(info.st_mode), 'uid': info.st_uid,
            'gid': info.st_gid, 'mtime_ns': info.st_mtime_ns}


def identity(path):
    info = path.lstat()
    return info.st_dev, info.st_ino


@contextmanager
def owned_lock(root):
    lock = root / '.rollback.lock'
    try:
        lock.mkdir(mode=0o700)
    except FileExistsError as exc:
        raise Refusal('Lock already exists; do not remove another owner\'s lock') from exc
    lock_id, owner_id = identity(lock), None
    owner = lock / 'owner.json'
    owner_text = json.dumps({'pid': os.getpid()})
    try:
        with owner.open('x', encoding='utf-8') as stream:
            owner_id = identity(owner)
            stream.write(owner_text)
        yield
    finally:
        # Leave any replaced lock or unexpected contents for manual inspection.
        if identity(lock) != lock_id or set(lock.iterdir()) - {owner}:
            raise Refusal('Lock changed; retained for manual reconciliation')
        if owner_id is not None:
            if identity(owner) != owner_id or owner.read_text(encoding='utf-8') != owner_text:
                raise Refusal('Lock owner changed; retained for manual reconciliation')
            owner.unlink()
        lock.rmdir()


def rollback(*, root, records, backup, original_sha256, config_sha256,
             cache_sha256, writers_stopped=False):
    if os.name != 'posix':
        raise Refusal('This reference requires POSIX; Windows metadata semantics are not supported')
    if not writers_stopped:
        raise Refusal('Stop/exclude ALL writers through verification before acknowledging --writers-stopped')
    for value in (original_sha256, config_sha256, cache_sha256):
        if not re.fullmatch(r'[0-9a-f]{64}', value):
            raise Refusal('Expected a lowercase SHA-256 digest')
    root, records = physical(root, True), physical(records, True)
    backup = physical(backup)
    if records.is_relative_to(root) or backup.is_relative_to(root):
        raise Refusal('Backup and verification records must be outside the rollback root')
    config, cache = root / 'config.md', root / 'cache'
    new = cache / 'new.json'
    journal = None

    def record(stage, **data):
        journal.write(json.dumps({'stage': stage, **data}) + '\n')
        journal.flush()
        os.fsync(journal.fileno())

    try:
        with owned_lock(root):
            # All expected states must validate before any target mutation.
            physical(cache, True)
            for path in (backup, config, new):
                physical(path)
            original, installed, created = image(backup), image(config), image(new)
            if (original['sha256'], installed['sha256'], created['sha256']) != (
                    original_sha256, config_sha256, cache_sha256):
                raise Refusal('Backup or postimage checksum conflict; no target changed')
            fd, receipt = tempfile.mkstemp(prefix='rollback-', suffix='.jsonl', dir=records)
            journal = os.fdopen(fd, 'w', encoding='utf-8')
            record('validated', root=str(root), backup=str(backup), original=original,
                   postimages={'config': installed, 'cache_file': created},
                   writer_exclusion='caller acknowledged, not enforced by this lock')
            temporary, temp_id = None, None
            try:
                fd, name = tempfile.mkstemp(prefix='.config-restore-', dir=root)
                temporary = Path(name)
                temp_id = identity(temporary)
                with os.fdopen(fd, 'wb') as stream:
                    stream.write(backup.read_bytes())
                    stream.flush()
                    current = os.fstat(stream.fileno())
                    if (current.st_uid, current.st_gid) != (original['uid'], original['gid']):
                        os.fchown(stream.fileno(), original['uid'], original['gid'])
                    os.fchmod(stream.fileno(), original['mode'])
                    os.utime(stream.fileno(), ns=(original['mtime_ns'], original['mtime_ns']))
                    os.fsync(stream.fileno())
                if image(temporary) != original:
                    raise Refusal('Prepared restoration differs from original backup')
                os.replace(temporary, config)
                temporary = None
                record('restored', config=image(config))
                new.unlink()
                # Never recursively remove a newly created but now populated directory.
                retained = bool(list(cache.iterdir()))
                if not retained:
                    cache.rmdir()
                if (image(config) != original or os.path.lexists(new)
                        or cache.exists() != retained or image(backup) != original):
                    raise Refusal('Final state mismatch; inspect retained evidence before retrying')
                record('verified', config=image(config), cache_directory_retained=retained,
                       created_file_absent=True, backup_preserved=True)
            finally:
                if temporary is not None:
                    if identity(temporary) != temp_id:
                        raise Refusal('Restore temporary changed; retained for manual reconciliation')
                    temporary.unlink()
        # Completion requires successful verification AND lock cleanup.
        record('complete', receipt=str(receipt))
        return {'status': 'complete', 'receipt': str(receipt), 'cache_directory_retained': retained}
    except BaseException as exc:
        if journal is not None:
            try:
                record('failed', error=str(exc), action='manual reconciliation; never infer prior success')
            except OSError:
                pass  # Preserve the original error if evidence storage itself failed.
        raise
    finally:
        if journal is not None:
            journal.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ('root', 'records', 'backup', 'original-sha256', 'config-sha256', 'cache-sha256'):
        parser.add_argument('--' + flag, required=True)
    parser.add_argument('--writers-stopped', action='store_true',
                        help='Acknowledge externally enforced exclusion of every writer, NOT just this lock')
    args = parser.parse_args()
    try:
        result = rollback(**vars(args))
    except Refusal as exc:
        print('REFUSED: ' + str(exc) + '; targets may already have changed; '
              'inspect retained evidence before retrying', file=sys.stderr)
        return 3
    except OSError as exc:
        print('FAILED: ' + str(exc) + '; inspect retained evidence before retrying', file=sys.stderr)
        return 4
    print(json.dumps(result))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
