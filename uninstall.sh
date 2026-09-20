#!/usr/bin/env bash
# DocForge uninstaller (Linux/macOS).
set -euo pipefail

PURGE=""
for arg in "$@"; do
  case "$arg" in
    --purge) PURGE="--purge" ;;
    --dry-run) DRY="--dry-run" ;;
  esac
done

if command -v docforge >/dev/null 2>&1; then
  exec docforge uninstall ${DRY:-} ${PURGE}
fi
# Fallback: run via Python module
PY="$(command -v python3 || command -v python)"
if [ -z "$PY" ]; then
  echo "python3 requis." >&2
  exit 1
fi
exec "$PY" -m docforge.cli uninstall ${DRY:-} ${PURGE}
