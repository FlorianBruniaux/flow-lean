# Executable rollback checks

`scripts/check_rollback.py` checks a locally reviewed rollback program in nine
disposable fixture scenarios. It does not invoke a model. It replaces the local
v2 pilot's one-off probes with reusable assertions and a machine-readable verdict.
The generated rollback is the subject under test; the checker is not a rollback
implementation to install in a project.

| Scenario | Required behavior |
| --- | --- |
| `normal` | Restore original contents and POSIX mode, remove the created file and empty directory, keep evidence, release the owned lock. |
| `config_conflict` | Nonzero exit before changing either target or the cache directory; preserve the concurrent configuration. |
| `cache_conflict` | Nonzero exit before changing either target or directory; preserve the concurrent cache. |
| `missing_target` | Treat an absent expected postimage as conflict, with no earlier mutation. |
| `unrelated_temp` | Preserve a preexisting `config.md.rollback.tmp` while completing rollback. |
| `held_lock` | Refuse without target mutation; preserve the other owner's lock identity. |
| `nonempty_cache` | Remove only the created file; retain the directory and its unrelated contents. |
| `invalid_backup` | Refuse before any target mutation when the backup hash is wrong. |
| `missing_backup` | Refuse before any target mutation when no backup is available. |

Every scenario also checks the backup, prior evidence and unrelated fixture
paths. Success requires a new nonempty evidence file outside removed paths.
Evidence presence is not proof that the log describes the outcome truthfully;
review its contents separately. Timeout, missing executable, source drift and
failed assertions never count as PASS. Previously saved reports are not replaced.

## Adapter contract

Use a JSON adapter with an argv array, the reviewed source files and the lock
convention. Paths to the program and its source files must be absolute because
execution uses a disposable working directory. No shell interpolation is used.

The following is an example format, not a runnable installed-program path:

```json
{
  "command": ["python3", "/absolute/reviewed-rollback.py", "--root", "{root}",
              "--verify-dir", "{records}", "--backup", "{backup}",
              "--original-sha", "{original_sha256}",
              "--config-sha", "{config_sha256}", "--cache-sha", "{cache_sha256}"],
  "source_files": ["/absolute/reviewed-rollback.py"],
  "lock_kind": "directory",
  "lock_path": "{root}/.rollback.lock",
  "timeout_seconds": 10
}
```

Supported lock kinds are `directory`, `flock`, and `exclusive_file` (atomic
exclusive creation). For the last kind, `held_lock_text` can supply the program's
documented ownership payload; it must represent an already-held lock. For a directory lock, add any
supported zero-timeout flag to the command to avoid waiting on the held-lock
fixture. A persistent flock support file is allowed; the checker tests whether
the lock can actually be acquired after the process exits. The adapter must map
the exact lock used by the program, not a second lock introduced for the test.

If a program explicitly documents a nonzero completion status for a retained
nonempty directory, declare it in the adapter, for example
`"success_codes": {"nonempty_cache": [0, 6]}`. This affects the exit-code check
only. Content, metadata, unrelated files, evidence and locks must still satisfy
every state assertion. Conflict scenarios cannot receive success-code overrides.
Record this policy before executing the program, not after inspecting its score.

Include local imported code in `source_files` when it affects the program.
Hashes are recorded before and after the probes. This detects lasting source
drift, not a change-and-restore race or changes to undeclared dependencies.

```bash
python3 scripts/check_rollback.py evals/local/reviewed-adapter.json \
  --reviewed --output evals/local/new-rollback-report.json
```

This executes the supplied program. Inspect its code and adapter first: a
temporary directory and the `--reviewed` acknowledgment are **not a sandbox**.
Do not point an unreviewed generated program at this harness or provide it with
real application paths. The checker does not restrict network or filesystem
access by the child. Run hostile programs only in separately managed isolation.

## Coverage and limits

The unit suite uses a controlled program and deliberate defects. It proves the
checker rejects leaked locks, removal of another owner's lock, partial mutation
on conflicts, temporary-file overwrite, no-op success, empty or deleted evidence,
wrong POSIX mode, and deletion of unrelated cache contents. These fixtures are
test doubles, not model outputs or production-safe rollback implementations.

The nine scenarios do not prove coordination with every writer, atomicity under
races, crash recovery, symlink safety, ownership/ACL restoration, metadata beyond
POSIX mode, or rollback after every possible I/O failure. Review those properties
when the target environment requires them. No live writer race is exercised.
Windows skips mode assertions and reports that scope as UNKNOWN. Flock scenarios
are UNKNOWN outside POSIX. Local PASS applies only to the executed assertions.

The new probes are development tests informed by the v2 failures. Keep original
v2 receipts unchanged and store any replay under a new report path. Do not fold
these extra checks into a historical score as if they had been preregistered.

On 2026-10-17 the four saved v2 scripts were replayed unchanged through all nine
scenarios (36 executions, no model calls). The checker reproduced the known lock,
temporary-file and conflict defects. It also rejected all four scripts when an
expected target was missing, and rejected the generic and baseline scripts on an
invalid backup. These are retrospective development findings, not v3 results.
Local receipts are at `evals/local/rollback-v3-replay-2026-10-17.json` (ignored by
Git). Source hashes before and after the replay match for all four scripts.

## V3.1 development probes

The checker now also refuses `missing_config`, `config_symlink` and
`cache_symlink` before mutation. Together with `missing_target`, these cover
absence and symlink substitution for both targets. Existing nine-scenario
campaign receipts retain their original scope; they are not retroactively
reported as twelve-scenario runs. The manually repaired v3 witness and its
Bash 3.2 argument checks are documented in [V3.1 preparation](V3.1-PREPARATION.md).
