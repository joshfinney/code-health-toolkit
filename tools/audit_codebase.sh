#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="${1:-.}"
AUDIT_DIR="${AUDIT_DIR:-.audit}"
CODE_HEALTH_PATHS="${CODE_HEALTH_PATHS:-src tests}"
PYTHON_RUNNER="${PYTHON_RUNNER:-}"

cd "$ROOT_DIR"
mkdir -p "$AUDIT_DIR"

STATUS_FILE="$AUDIT_DIR/status.tsv"
MANIFEST_FILE="$AUDIT_DIR/manifest.txt"

: > "$STATUS_FILE"

{
  printf 'code-health audit\n'
  printf 'root=%s\n' "$(pwd)"
  printf 'audit_dir=%s\n' "$AUDIT_DIR"
  printf 'paths=%s\n' "$CODE_HEALTH_PATHS"
  printf 'timestamp_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$MANIFEST_FILE"

note() {
  printf '%s\n' "$*" >&2
}

record_status() {
  local name="$1"
  local status="$2"
  local output="$3"
  printf '%s\t%s\t%s\n' "$name" "$status" "$output" >> "$STATUS_FILE"
}

have() {
  command -v "$1" >/dev/null 2>&1
}

detect_python_runner() {
  if [[ -n "$PYTHON_RUNNER" ]]; then
    printf '%s\n' "$PYTHON_RUNNER"
  elif have uv; then
    printf 'uv run'
  elif have python3; then
    printf 'python3 -m'
  else
    printf 'python -m'
  fi
}

run_check() {
  local name="$1"
  local output="$2"
  shift 2

  note "== $name =="
  set +e
  "$@" > "$output" 2> "$output.stderr"
  local status=$?
  set -e

  if [[ -s "$output.stderr" ]]; then
    printf '\n[stderr]\n' >> "$output"
    cat "$output.stderr" >> "$output"
  fi
  rm -f "$output.stderr"

  record_status "$name" "$status" "$output"
  return 0
}

run_shell_check() {
  local name="$1"
  local output="$2"
  local command="$3"

  note "== $name =="
  set +e
  bash -lc "$command" > "$output" 2> "$output.stderr"
  local status=$?
  set -e

  if [[ -s "$output.stderr" ]]; then
    printf '\n[stderr]\n' >> "$output"
    cat "$output.stderr" >> "$output"
  fi
  rm -f "$output.stderr"

  record_status "$name" "$status" "$output"
  return 0
}

RUNNER="$(detect_python_runner)"

run_shell_check "ruff check" "$AUDIT_DIR/ruff.json" \
  "$RUNNER ruff check $CODE_HEALTH_PATHS --output-format=json"

run_shell_check "ruff format" "$AUDIT_DIR/ruff-format.txt" \
  "$RUNNER ruff format --check $CODE_HEALTH_PATHS"

run_shell_check "pyright" "$AUDIT_DIR/pyright.json" \
  "$RUNNER pyright --outputjson"

run_shell_check "pytest coverage" "$AUDIT_DIR/coverage.txt" \
  "$RUNNER pytest --cov=src --cov-branch --cov-report=term-missing --cov-report=html:$AUDIT_DIR/htmlcov"

run_shell_check "vulture" "$AUDIT_DIR/vulture.txt" \
  "$RUNNER vulture $CODE_HEALTH_PATHS --min-confidence 80 --sort-by-size"

run_shell_check "deptry" "$AUDIT_DIR/deptry.txt" \
  "$RUNNER deptry ."

run_shell_check "radon complexity" "$AUDIT_DIR/radon-cc.json" \
  "$RUNNER radon cc src -s -a -j"

run_shell_check "radon raw" "$AUDIT_DIR/radon-raw.json" \
  "$RUNNER radon raw src -j"

run_shell_check "import-linter" "$AUDIT_DIR/import-linter.txt" \
  "$RUNNER lint-imports"

run_shell_check "bandit" "$AUDIT_DIR/bandit.json" \
  "$RUNNER bandit -r src -f json"

run_shell_check "pip-audit" "$AUDIT_DIR/pip-audit.json" \
  "$RUNNER pip-audit --format=json"

if have jscpd; then
  mkdir -p "$AUDIT_DIR/jscpd"
  run_check "jscpd duplication" "$AUDIT_DIR/jscpd/output.txt" \
    jscpd src --reporters json --output "$AUDIT_DIR/jscpd"
else
  note "== jscpd duplication =="
  printf 'jscpd not found; skipped\n' > "$AUDIT_DIR/jscpd.txt"
  record_status "jscpd duplication" "127" "$AUDIT_DIR/jscpd.txt"
fi

note "Audit complete. See $AUDIT_DIR/"
note "Status summary: $STATUS_FILE"

