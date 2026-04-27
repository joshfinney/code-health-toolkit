#!/usr/bin/env bash
set -Eeuo pipefail

if [[ $# -ne 1 ]]; then
  printf 'usage: %s /path/to/target-repo\n' "$0" >&2
  exit 2
fi

TARGET_DIR="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLKIT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ ! -d "$TARGET_DIR/.git" ]]; then
  printf 'target must be a git repository: %s\n' "$TARGET_DIR" >&2
  exit 1
fi

mkdir -p "$TARGET_DIR/tools" "$TARGET_DIR/docs"

install_file() {
  local source="$1"
  local destination="$2"
  if [[ -e "$destination" ]]; then
    printf 'exists, leaving unchanged: %s\n' "$destination" >&2
    return 0
  fi
  cp "$source" "$destination"
  printf 'created: %s\n' "$destination" >&2
}

install_file "$TOOLKIT_DIR/tools/audit_codebase.sh" "$TARGET_DIR/tools/audit_codebase.sh"
install_file "$TOOLKIT_DIR/tools/rank_hotspots.py" "$TARGET_DIR/tools/rank_hotspots.py"
install_file "$TOOLKIT_DIR/templates/AGENTS.md" "$TARGET_DIR/AGENTS.md"
install_file "$TOOLKIT_DIR/templates/importlinter.ini" "$TARGET_DIR/importlinter.ini"
install_file "$TOOLKIT_DIR/templates/pyproject-code-health.toml" "$TARGET_DIR/docs/pyproject-code-health.toml"

chmod +x "$TARGET_DIR/tools/audit_codebase.sh" "$TARGET_DIR/tools/rank_hotspots.py"

if [[ -f "$TARGET_DIR/.gitignore" ]]; then
  if ! grep -qxF '.audit/' "$TARGET_DIR/.gitignore"; then
    printf '\n.audit/\n' >> "$TARGET_DIR/.gitignore"
    printf 'updated: %s\n' "$TARGET_DIR/.gitignore" >&2
  fi
else
  printf '.audit/\n' > "$TARGET_DIR/.gitignore"
  printf 'created: %s\n' "$TARGET_DIR/.gitignore" >&2
fi

printf '\nNext steps:\n' >&2
printf '  cd %s\n' "$TARGET_DIR" >&2
printf '  git switch -c refactor/code-health-baseline\n' >&2
printf '  ./tools/audit_codebase.sh\n' >&2
printf '  python tools/rank_hotspots.py --audit-dir .audit --output-md .audit/hotspots.md\n' >&2

