#!/usr/bin/env bash
# rollback-config.sh
# Rolls back a local update: restores ROOT/config.md from backup and removes
# ROOT/cache/new.json and ROOT/cache/ (both created by the update, absent before).
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  rollback-config.sh --root PATH --verify-dir PATH --config-backup PATH \
    --orig-checksum SHA256 --installed-config-checksum SHA256 \
    --installed-newjson-checksum SHA256

  rollback-config.sh --self-test

Prerequisite (do this BEFORE running, not optional):
  Stop or pause any other process that writes ROOT/config.md or
  ROOT/cache/new.json. This script excludes writers only via a cooperative
  lock directory (ROOT/.rollback.lock); it cannot force an external process
  to honor it.

Arguments:
  --root PATH                          directory containing config.md, cache/
  --verify-dir PATH                    directory OUTSIDE --root for evidence logs
  --config-backup PATH                 pre-update content to restore into config.md
  --orig-checksum SHA256               checksum of --config-backup
  --installed-config-checksum SHA256   expected current checksum of ROOT/config.md
  --installed-newjson-checksum SHA256  expected current checksum of ROOT/cache/new.json

Exit codes: 0 success | 1 argument/usage error | 2 lock held (another
operation active) | 3 conflict detected before any mutation, nothing changed
| 4 post-mutation verification failed, manual reconciliation required.
EOF
}

die() { echo "ERROR: $1" >&2; exit "${2:-1}"; }

checksum_of() {
  local f="$1"
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$f" | awk '{print $1}'
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$f" | awk '{print $1}'
  else
    die "need sha256sum or shasum in PATH" 1
  fi
}

do_rollback() {
  local root="$1" verify_dir="$2" config_backup="$3" orig_checksum="$4" \
        installed_config_checksum="$5" installed_newjson_checksum="$6"

  [[ -n "$root" && -n "$verify_dir" && -n "$config_backup" && -n "$orig_checksum" \
     && -n "$installed_config_checksum" && -n "$installed_newjson_checksum" ]] \
    || die "missing required argument (see --help)" 1

  [[ -d "$root" && ! -L "$root" ]] || die "ROOT is not a plain directory: $root" 3
  mkdir -p "$verify_dir" || die "cannot create verify-dir: $verify_dir" 1
  [[ -d "$verify_dir" && ! -L "$verify_dir" ]] || die "verify-dir is not a plain directory" 1
  local root_real verify_real
  root_real="$(cd "$root" && pwd -P)"
  verify_real="$(cd "$verify_dir" && pwd -P)"
  case "$verify_real/" in
    "$root_real"/*) die "--verify-dir must be outside --root" 1 ;;
  esac

  [[ -f "$config_backup" && ! -L "$config_backup" ]] \
    || die "config backup missing or not a regular file: $config_backup" 3
  local backup_sum; backup_sum="$(checksum_of "$config_backup")"
  [[ "$backup_sum" == "$orig_checksum" ]] \
    || die "backup checksum mismatch: expected $orig_checksum got $backup_sum" 3

  local config="$root/config.md"
  local cache_dir="$root/cache"
  local newjson="$cache_dir/new.json"
  local lock_dir="$root/.rollback.lock"
  local created_tmp=""

  # Prerequisite enforcement: cooperative exclusive lock.
  if ! mkdir "$lock_dir" 2>/dev/null; then
    die "lock held ($lock_dir): another operation may be active; stop it, or remove the lock manually once confirmed stale" 2
  fi
  cleanup() {
    [[ -n "$created_tmp" && -e "$created_tmp" ]] && rm -f "$created_tmp"
    rmdir "$lock_dir" 2>/dev/null || true
  }
  trap cleanup EXIT

  # Pre-mutation validation of current (possibly writer-modified) state.
  [[ -f "$config" && ! -L "$config" ]] \
    || die "ROOT/config.md missing or not a regular file; refusing" 3
  local cur_config_sum; cur_config_sum="$(checksum_of "$config")"
  [[ "$cur_config_sum" == "$installed_config_checksum" ]] \
    || die "ROOT/config.md checksum mismatch: expected $installed_config_checksum got $cur_config_sum (concurrent write?)" 3

  [[ -d "$cache_dir" && ! -L "$cache_dir" ]] \
    || die "ROOT/cache missing or not a plain directory; refusing" 3
  [[ -f "$newjson" && ! -L "$newjson" ]] \
    || die "ROOT/cache/new.json missing or not a regular file; refusing" 3
  local cur_newjson_sum; cur_newjson_sum="$(checksum_of "$newjson")"
  [[ "$cur_newjson_sum" == "$installed_newjson_checksum" ]] \
    || die "ROOT/cache/new.json checksum mismatch: expected $installed_newjson_checksum got $cur_newjson_sum (concurrent write?)" 3

  local extra; extra="$(find "$cache_dir" -mindepth 1 ! -name new.json)"
  [[ -z "$extra" ]] \
    || die "ROOT/cache has unexpected entries not created by this update; stop for manual reconciliation: $extra" 3

  local ts; ts="$(date -u +%Y%m%dT%H%M%SZ)"
  {
    echo "timestamp=$ts"
    echo "root=$root_real"
    echo "config_checksum_before=$cur_config_sum"
    echo "newjson_checksum_before=$cur_newjson_sum"
  } >> "$verify_dir/pre-rollback-$ts.log"

  # Mutation 1: restore config.md via temp file + atomic rename (never truncate in place).
  created_tmp="$(mktemp "$root/.config.md.rollback.XXXXXX")"
  cp "$config_backup" "$created_tmp"
  local tmp_sum; tmp_sum="$(checksum_of "$created_tmp")"
  [[ "$tmp_sum" == "$orig_checksum" ]] || die "restore temp file checksum mismatch, aborting before mutation" 3
  mv -f "$created_tmp" "$config"
  created_tmp=""

  # Mutation 2: remove the created file, then the created directory only if empty.
  rm -f "$newjson"
  rmdir "$cache_dir" 2>/dev/null \
    || die "ROOT/cache not empty after removing new.json; left as-is, manual reconciliation required" 4

  # Post-mutation verification.
  [[ -f "$config" ]] || die "post-check: config.md missing after restore" 4
  local final_sum; final_sum="$(checksum_of "$config")"
  [[ "$final_sum" == "$orig_checksum" ]] || die "post-check: config.md checksum mismatch after restore" 4
  [[ ! -e "$newjson" && ! -d "$cache_dir" ]] || die "post-check: cache/new.json or cache/ still present" 4

  {
    echo "timestamp=$(date -u +%Y%m%dT%H%M%SZ)"
    echo "config_checksum_after=$final_sum"
    echo "result=rollback_complete"
  } >> "$verify_dir/post-rollback-$ts.log"

  echo "Rollback complete. config.md restored (sha256 $final_sum); cache/new.json and cache/ removed."
  echo "Evidence: $verify_dir/pre-rollback-$ts.log, $verify_dir/post-rollback-$ts.log"
}

self_test() {
  local sandbox out failures=0
  sandbox="$(mktemp -d)"
  out="$(mktemp)"

  run_case() {
    local desc="$1" expected_rc="$2"; shift 2
    local rc=0
    bash "$0" "$@" >"$out" 2>&1 || rc=$?
    if [[ "$rc" -eq "$expected_rc" ]]; then
      echo "PASS: $desc (rc=$rc)"
    else
      echo "FAIL: $desc (expected rc=$expected_rc got rc=$rc)"; cat "$out" >&2
      failures=$((failures + 1))
    fi
  }

  setup_case() {
    CASE_ROOT="$(mktemp -d "$sandbox/root.XXXXXX")"
    CASE_VERIFY="$(mktemp -d "$sandbox/verify.XXXXXX")"
    CASE_BACKUP="$sandbox/backup-$RANDOM.md"
    echo "original content $RANDOM" > "$CASE_BACKUP"
    ORIG_SUM="$(checksum_of "$CASE_BACKUP")"
    echo "installed content $RANDOM" > "$CASE_ROOT/config.md"
    CONFIG_SUM="$(checksum_of "$CASE_ROOT/config.md")"
    mkdir "$CASE_ROOT/cache"
    echo '{"k":1}' > "$CASE_ROOT/cache/new.json"
    NEWJSON_SUM="$(checksum_of "$CASE_ROOT/cache/new.json")"
  }

  setup_case
  run_case "success path" 0 \
    --root "$CASE_ROOT" --verify-dir "$CASE_VERIFY" --config-backup "$CASE_BACKUP" \
    --orig-checksum "$ORIG_SUM" --installed-config-checksum "$CONFIG_SUM" \
    --installed-newjson-checksum "$NEWJSON_SUM"
  if [[ -f "$CASE_ROOT/config.md" && ! -e "$CASE_ROOT/cache" \
        && "$(checksum_of "$CASE_ROOT/config.md")" == "$ORIG_SUM" \
        && ! -d "$CASE_ROOT/.rollback.lock" ]]; then
    echo "PASS: final state matches backup, cache removed, lock released"
  else
    echo "FAIL: final state incorrect"; failures=$((failures + 1))
  fi

  setup_case; rm -f "$CASE_ROOT/config.md"
  run_case "missing config.md -> conflict" 3 \
    --root "$CASE_ROOT" --verify-dir "$CASE_VERIFY" --config-backup "$CASE_BACKUP" \
    --orig-checksum "$ORIG_SUM" --installed-config-checksum "$CONFIG_SUM" \
    --installed-newjson-checksum "$NEWJSON_SUM"

  setup_case; echo "tampered by another process" >> "$CASE_ROOT/config.md"
  run_case "concurrent edit -> conflict" 3 \
    --root "$CASE_ROOT" --verify-dir "$CASE_VERIFY" --config-backup "$CASE_BACKUP" \
    --orig-checksum "$ORIG_SUM" --installed-config-checksum "$CONFIG_SUM" \
    --installed-newjson-checksum "$NEWJSON_SUM"

  setup_case; rm -rf "$CASE_ROOT/cache"; ln -s /tmp "$CASE_ROOT/cache"
  run_case "cache replaced by symlink -> conflict" 3 \
    --root "$CASE_ROOT" --verify-dir "$CASE_VERIFY" --config-backup "$CASE_BACKUP" \
    --orig-checksum "$ORIG_SUM" --installed-config-checksum "$CONFIG_SUM" \
    --installed-newjson-checksum "$NEWJSON_SUM"

  setup_case
  run_case "invalid backup checksum -> conflict" 3 \
    --root "$CASE_ROOT" --verify-dir "$CASE_VERIFY" --config-backup "$CASE_BACKUP" \
    --orig-checksum "deadbeef" --installed-config-checksum "$CONFIG_SUM" \
    --installed-newjson-checksum "$NEWJSON_SUM"

  setup_case; echo "other" > "$CASE_ROOT/cache/other.txt"
  run_case "unexpected cache content -> conflict" 3 \
    --root "$CASE_ROOT" --verify-dir "$CASE_VERIFY" --config-backup "$CASE_BACKUP" \
    --orig-checksum "$ORIG_SUM" --installed-config-checksum "$CONFIG_SUM" \
    --installed-newjson-checksum "$NEWJSON_SUM"

  setup_case; mkdir "$CASE_ROOT/.rollback.lock"
  run_case "lock held -> refusal" 2 \
    --root "$CASE_ROOT" --verify-dir "$CASE_VERIFY" --config-backup "$CASE_BACKUP" \
    --orig-checksum "$ORIG_SUM" --installed-config-checksum "$CONFIG_SUM" \
    --installed-newjson-checksum "$NEWJSON_SUM"
  if [[ "$(checksum_of "$CASE_ROOT/config.md")" == "$CONFIG_SUM" ]]; then
    echo "PASS: targets untouched while lock held"
  else
    echo "FAIL: targets mutated despite lock"; failures=$((failures + 1))
  fi
  rmdir "$CASE_ROOT/.rollback.lock"

  rm -rf "$sandbox" "$out"
  if [[ $failures -eq 0 ]]; then
    echo "SELF-TEST: all cases passed"; return 0
  else
    echo "SELF-TEST: $failures case(s) failed"; return 1
  fi
}

ROOT="" VERIFY_DIR="" CONFIG_BACKUP="" ORIG_CHECKSUM=""
INSTALLED_CONFIG_CHECKSUM="" INSTALLED_NEWJSON_CHECKSUM="" SELF_TEST=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root) ROOT="$2"; shift 2 ;;
    --verify-dir) VERIFY_DIR="$2"; shift 2 ;;
    --config-backup) CONFIG_BACKUP="$2"; shift 2 ;;
    --orig-checksum) ORIG_CHECKSUM="$2"; shift 2 ;;
    --installed-config-checksum) INSTALLED_CONFIG_CHECKSUM="$2"; shift 2 ;;
    --installed-newjson-checksum) INSTALLED_NEWJSON_CHECKSUM="$2"; shift 2 ;;
    --self-test) SELF_TEST=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ $SELF_TEST -eq 1 ]]; then
  self_test; exit $?
fi

do_rollback "$ROOT" "$VERIFY_DIR" "$CONFIG_BACKUP" "$ORIG_CHECKSUM" \
            "$INSTALLED_CONFIG_CHECKSUM" "$INSTALLED_NEWJSON_CHECKSUM"
