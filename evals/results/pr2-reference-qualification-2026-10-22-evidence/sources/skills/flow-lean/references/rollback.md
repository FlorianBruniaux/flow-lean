# Bounded rollback reference

Use [rollback_reference.py](../scripts/rollback_reference.py) for this exact case: `config.md` existed before installation; `cache/new.json` and `cache/` were created by it. The caller supplies the original backup with original metadata, its SHA-256 and both installed file checksums. Other rollback layouts require a reviewed adaptation and their own tests. Do not generalize this reference into a claim that arbitrary rollback is safe.

1. Exclude every writer externally for the full check/restore/verify interval. `--writers-stopped` acknowledges that prerequisite; it does not enforce it. The directory lock coordinates only callers honoring this same protocol. Without exclusion, stop for manual reconciliation. Never remove an existing lock merely because its PID appears stale.
2. Review the inputs and scope. Require Python 3.9+ on POSIX, physical absolute paths without symlink components or `..`, existing records directory and backup outside the root, single-link regular target/backup files, and the original backup's mode, UID, GID and modification time. Check the required ownership can be restored. The reference does not preserve ACLs, extended attributes, birth time, atime or hardlinks; if any are required, stop and adapt before use.
3. Run only after the above prerequisites and task authorization are satisfied. It validates backup and both postimages before modifying a target, prepares an exclusively created temporary file, verifies its bytes/metadata, restores `config.md`, removes only the unchanged `new.json`, and removes `cache/` only when empty. A populated directory is retained successfully. Receipt stages remain outside the root; earlier evidence and backup are preserved.
4. Require exit 0, a `complete` receipt, verified final content/metadata, and release of this invocation's lock before reporting completion. Exit 2 means argument error, 3 refusal, 4 I/O failure. Partial restoration can occur after a later I/O failure: inspect receipts and reconcile manually, never claim all-or-nothing behavior or retry automatically. Even an original-looking tree is refused on another run; receipt-based idempotent replay is not implemented.

Example argument shape, not permission to run (replace paths and digests with verified values):

```bash
python3 /physical/path/to/rollback_reference.py \
  --root /physical/worktree \
  --records /physical/verification \
  --backup /physical/backups/config.md \
  --original-sha256 ORIGINAL_SHA256 \
  --config-sha256 INSTALLED_CONFIG_SHA256 \
  --cache-sha256 INSTALLED_CACHE_SHA256 \
  --writers-stopped
```

On macOS, `/tmp` and `/var` may be aliases. Obtain the physical base before recording installation paths, then validate every path component; do not resolve a substituted target link as a way to make it pass. The script refuses aliases instead of silently following them.

The implementation is a bounded reference, not a filesystem transaction or a crash-recovery mechanism. It records verified stages with file fsync, but does not promise directory-entry durability after power loss. Process termination can leave a lock or a temporary file for manual inspection. Cooperative exclusion and access control remain deployment prerequisites, not properties proved by hash comparison. Preserve a changed lock or unexpected contents rather than deleting another owner's state.

Run the repository's `tests/test_reference_rollback.py` and the 18-scenario checker on any adaptation. Those checks cover successful restoration, missing/conflicting/type/link targets, temporary-name collisions, lock lifetime, nonempty directories, argument errors and selected I/O faults. They do not establish Windows compatibility, every race, every I/O failure or native model adherence.
