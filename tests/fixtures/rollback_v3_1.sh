#!/usr/bin/env bash
# Offline regression witness manually repaired from the v3 pilot.
# NOT a general-purpose or production rollback installer.
set -euo pipefail

# ---------------------------------------------------------------------------
# Usage / argument parsing
# ---------------------------------------------------------------------------
usage() {
  cat <<'EOF'
Usage: rollback.sh \
  --root <path> \
  --verify-dir <path> \
  --backup <path-to-original-config.md> \
  --orig-checksum <sha256-of-original-config.md> \
  --installed-config-checksum <sha256-of-config.md-as-installed> \
  --installed-cache-checksum <sha256-of-cache/new.json-as-installed> \
  [--lock-dir <path>]           (default: <root>/.rollback.lock)
  [--lock-wait-seconds <n>]     (default: 30)

Exit codes:
  0  full rollback: config.md restored, cache/new.json and cache/ removed
  1  usage/environment error (bad args, missing deps, unwritable verify-dir) — no mutation attempted
  2  backup file failed checksum validation — no mutation attempted
  3  config.md does not match the expected installed checksum (concurrent writer) — no mutation attempted
  4  cache/new.json does not match the expected installed checksum (concurrent writer) — no mutation attempted
  5  could not acquire lock within --lock-wait-seconds — another writer/rollback is active
  6  config.md restored (and cache/new.json removed) but cache/ directory left in place
     because it still contains other files — partial result, manual check needed
EOF
}

ROOT="" VERIFY_DIR="" BACKUP="" ORIG_CHECKSUM="" INSTALLED_CONFIG_CHECKSUM="" INSTALLED_CACHE_CHECKSUM=""
LOCK_DIR="" LOCK_WAIT_SECONDS=30

while [ $# -gt 0 ]; do
  case "$1" in -h|--help) ;; *)
    [ $# -ge 2 ] || { echo "Missing value for $1" >&2; exit 1; } ;; esac
  case "$1" in
    --root) ROOT="$2"; shift 2 ;;
    --verify-dir) VERIFY_DIR="$2"; shift 2 ;;
    --backup) BACKUP="$2"; shift 2 ;;
    --orig-checksum) ORIG_CHECKSUM="$2"; shift 2 ;;
    --installed-config-checksum) INSTALLED_CONFIG_CHECKSUM="$2"; shift 2 ;;
    --installed-cache-checksum) INSTALLED_CACHE_CHECKSUM="$2"; shift 2 ;;
    --lock-dir) LOCK_DIR="$2"; shift 2 ;;
    --lock-wait-seconds) LOCK_WAIT_SECONDS="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done

for v in ROOT VERIFY_DIR BACKUP ORIG_CHECKSUM INSTALLED_CONFIG_CHECKSUM INSTALLED_CACHE_CHECKSUM; do
  if [ -z "${!v}" ]; then echo "Missing required argument: ${v}" >&2; usage; exit 1; fi
done

CONFIG_PATH="$ROOT/config.md"
CACHE_DIR="$ROOT/cache"
CACHE_FILE="$CACHE_DIR/new.json"
LOCK_DIR="${LOCK_DIR:-$ROOT/.rollback.lock}"

[ -d "$ROOT" ] || { echo "Root path not found: $ROOT" >&2; exit 1; }
[ -d "$VERIFY_DIR" ] && [ -w "$VERIFY_DIR" ] || { echo "Verify-dir missing or not writable: $VERIFY_DIR" >&2; exit 1; }
[ -f "$BACKUP" ] && [ ! -L "$BACKUP" ] || { echo "Backup missing or substituted: $BACKUP" >&2; exit 1; }

sha256_of() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk '{print $1}'
  else
    echo "No sha256 tool (sha256sum/shasum) available" >&2
    return 1
  fi
}

record() {
  # $1 = phase tag (pre|post|conflict); rest of args = lines to write.
  local phase="$1"; shift
  local f
  f=$(mktemp "$VERIFY_DIR/rollback-${phase}-XXXXXXXX.log")
  {
    echo "timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "root: $ROOT"
    for line in "$@"; do echo "$line"; done
  } >"$f"
  echo "$f"
}

# ---------------------------------------------------------------------------
# Lock: coordination with other writers is a prerequisite. Any other process
# that writes config.md or cache/new.json must also acquire this same
# mkdir-based lock before writing, or run strictly outside this script's
# critical section. mkdir is atomic on all target platforms, which is why
# it is used as the lock primitive instead of a plain lock file.
# ---------------------------------------------------------------------------
LOCK_TOKEN="$(hostname 2>/dev/null || echo unknown)-$$-$(date +%s)-$RANDOM"
LOCK_ACQUIRED=0

acquire_lock() {
  local waited=0
  while ! mkdir "$LOCK_DIR" 2>/dev/null; do
    if [ "$waited" -ge "$LOCK_WAIT_SECONDS" ]; then
      echo "Could not acquire lock $LOCK_DIR within ${LOCK_WAIT_SECONDS}s" >&2
      exit 5
    fi
    sleep 1
    waited=$((waited + 1))
  done
  echo "$LOCK_TOKEN" >"$LOCK_DIR/owner"
  LOCK_ACQUIRED=1
}

release_lock() {
  [ "$LOCK_ACQUIRED" -eq 1 ] || return 0
  if [ -f "$LOCK_DIR/owner" ] && [ "$(cat "$LOCK_DIR/owner")" = "$LOCK_TOKEN" ]; then
    rm -f "$LOCK_DIR/owner"
    rmdir "$LOCK_DIR" 2>/dev/null || true
  fi
}
trap release_lock EXIT

acquire_lock

# A symlinked parent can redirect a regular leaf to unrelated work.
[ -d "$CACHE_DIR" ] && [ ! -L "$CACHE_DIR" ] || {
  echo "Cache directory missing or substituted; no changes made." >&2
  exit 4
}

# ---------------------------------------------------------------------------
# Validate backup integrity before touching anything.
# ---------------------------------------------------------------------------
backup_checksum="$(sha256_of "$BACKUP")"
if [ "$backup_checksum" != "$ORIG_CHECKSUM" ]; then
  record conflict \
    "stage: backup-validation" \
    "backup: $BACKUP" \
    "expected: $ORIG_CHECKSUM" \
    "actual: $backup_checksum" >/dev/null
  echo "Backup checksum mismatch — refusing to restore from a backup that does not match --orig-checksum" >&2
  exit 2
fi

pre_record="$(record pre \
  "stage: pre-rollback-snapshot" \
  "config_path: $CONFIG_PATH" \
  "cache_file: $CACHE_FILE")"
echo "Pre-rollback evidence written to: $pre_record"

# ---------------------------------------------------------------------------
# Concurrency check for config.md: only proceed if its current checksum
# still matches the checksum recorded right after installation. Any
# divergence means another process wrote to it after install, so its
# content must be preserved rather than overwritten.
# ---------------------------------------------------------------------------
if [ ! -f "$CONFIG_PATH" ] || [ -L "$CONFIG_PATH" ]; then
  current_config_checksum="(missing)"
else
  current_config_checksum="$(sha256_of "$CONFIG_PATH")"
fi

if [ "$current_config_checksum" != "$INSTALLED_CONFIG_CHECKSUM" ]; then
  record conflict \
    "stage: config-concurrency-check" \
    "path: $CONFIG_PATH" \
    "expected_installed: $INSTALLED_CONFIG_CHECKSUM" \
    "actual: $current_config_checksum" >/dev/null
  echo "config.md no longer matches the installed checksum — concurrent modification detected; no changes made. Manual reconciliation required." >&2
  exit 3
fi

# ---------------------------------------------------------------------------
# Both targets must match the recorded postimage. Absence is a conflict.
# ---------------------------------------------------------------------------
cache_present=0
cache_conflict=1
current_cache_checksum="(missing or wrong type)"
if [ -f "$CACHE_FILE" ] && [ ! -L "$CACHE_FILE" ]; then
  cache_conflict=0
  cache_present=1
  current_cache_checksum="$(sha256_of "$CACHE_FILE")"
  if [ "$current_cache_checksum" != "$INSTALLED_CACHE_CHECKSUM" ]; then
    cache_conflict=1
  fi
fi

if [ "$cache_conflict" -eq 1 ]; then
  record conflict \
    "stage: cache-concurrency-check" \
    "path: $CACHE_FILE" \
    "expected_installed: $INSTALLED_CACHE_CHECKSUM" \
    "actual: $current_cache_checksum" >/dev/null
  echo "cache/new.json no longer matches the installed checksum — concurrent modification detected; no changes made. Manual reconciliation required." >&2
  exit 4
fi

# ---------------------------------------------------------------------------
# Mutations start here. config.md is replaced via mktemp+mv so the
# replacement is atomic and no half-written file is ever visible.
# ---------------------------------------------------------------------------
tmp_config=$(mktemp "${CONFIG_PATH}.XXXXXXXX")
cp -p "$BACKUP" "$tmp_config"
restored_checksum="$(sha256_of "$tmp_config")"
if [ "$restored_checksum" != "$ORIG_CHECKSUM" ]; then
  rm -f "$tmp_config"
  echo "Internal error: staged restore copy does not match --orig-checksum, aborting before replacing config.md" >&2
  exit 1
fi
mv -f "$tmp_config" "$CONFIG_PATH"

if [ "$cache_present" -eq 1 ]; then
  rm -f "$CACHE_FILE"
fi

cache_dir_status="removed"
if [ -d "$CACHE_DIR" ]; then
  if ! rmdir "$CACHE_DIR" 2>/dev/null; then
    cache_dir_status="retained-nonempty"
  fi
else
  cache_dir_status="already-absent"
fi

final_config_checksum="$(sha256_of "$CONFIG_PATH")"
post_record="$(record post \
  "stage: post-rollback-verification" \
  "config_checksum: $final_config_checksum" \
  "config_expected: $ORIG_CHECKSUM" \
  "cache_file_status: $([ "$cache_present" -eq 1 ] && echo removed || echo already-absent)" \
  "cache_dir_status: $cache_dir_status" \
  "pre_evidence: $pre_record")"
echo "Post-rollback evidence written to: $post_record"

if [ "$final_config_checksum" != "$ORIG_CHECKSUM" ]; then
  echo "Post-restore verification failed: config.md does not match --orig-checksum after write" >&2
  exit 1
fi

if [ "$cache_dir_status" = "retained-nonempty" ]; then
  echo "Rollback partial: config.md restored; cache/ retained because it still contains other files (see $post_record)" >&2
  exit 6
fi

echo "Rollback complete: config.md restored, cache/new.json and cache/ removed ."
exit 0
