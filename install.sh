#!/usr/bin/env bash
# DocForge — bootstrap installer for Linux and macOS.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/dinaagz/DocForge/main/install.sh | bash
#
# Or from a local checkout:
#   ./install.sh              # normal user install
#   ./install.sh --dev        # editable dev install (uses this checkout)
#   DOCFORGE_HOME=/opt/df ./install.sh   # custom install location

set -euo pipefail

REPO="dinaagz/DocForge"
BRANCH="${DOCFORGE_BRANCH:-main}"
MODE="user"

for arg in "$@"; do
  case "$arg" in
    --dev)   MODE="dev" ;;
    --help)  echo "Usage: $0 [--dev]"; exit 0 ;;
  esac
done

info() { printf '  \033[36m›\033[0m %s\n' "$*"; }
ok()   { printf '  \033[32m✓\033[0m %s\n' "$*"; }
warn() { printf '  \033[33m!\033[0m %s\n' "$*" >&2; }
err()  { printf '  \033[31m✗\033[0m %s\n' "$*" >&2; }

echo "─────────────────────────────────────────────"
echo "  DocForge installer"
echo "─────────────────────────────────────────────"

# ── 1. Environment detection ─────────────────────────────
OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
ARCH="$(uname -m)"
info "OS:           $OS ($ARCH)"

PYTHON_BIN=""
for cand in python3.13 python3.12 python3.11 python3.10 python3.9 python3 python; do
  if command -v "$cand" >/dev/null 2>&1; then
    if "$cand" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' 2>/dev/null; then
      PYTHON_BIN="$(command -v "$cand")"
      break
    fi
  fi
done
if [ -z "$PYTHON_BIN" ]; then
  err "Aucun Python ≥ 3.9 détecté. Installez Python d'abord."
  exit 2
fi
PY_VER="$("$PYTHON_BIN" -c 'import sys; print("%d.%d.%d"%sys.version_info[:3])')"
info "Python:       $PYTHON_BIN ($PY_VER)"

# ── 2. Locate source tree ────────────────────────────────
HERE="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd 2>/dev/null || echo "")"
SOURCE=""
if [ -n "$HERE" ] && [ -f "$HERE/docforge/_version.py" ]; then
  SOURCE="$HERE"
elif [ "$MODE" = "dev" ]; then
  err "--dev requiert un checkout local ; ce script n'a pas trouvé le repo."
  exit 3
else
  info "Aucun checkout local détecté — téléchargement de $REPO@$BRANCH"
  TMP="$(mktemp -d)"
  URL="https://codeload.github.com/${REPO}/tar.gz/refs/heads/${BRANCH}"
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$URL" | tar -xz -C "$TMP"
  elif command -v wget >/dev/null 2>&1; then
    wget -qO- "$URL" | tar -xz -C "$TMP"
  else
    err "curl ou wget requis."
    exit 4
  fi
  SOURCE="$(find "$TMP" -maxdepth 2 -name '_version.py' -path '*/docforge/*' -exec dirname {} \; -quit)/.."
  SOURCE="$(cd "$SOURCE" && pwd)"
  ok  "Archive extraite dans $SOURCE"
fi

# ── 3. Ensure pip and virtualenv ─────────────────────────
export PYTHONDONTWRITEBYTECODE=1
if ! "$PYTHON_BIN" -m venv --help >/dev/null 2>&1; then
  err "Le module venv n'est pas disponible pour $PYTHON_BIN."
  exit 5
fi

# ── 4. Install into the runtime layout ───────────────────
info "Installation de DocForge…"
PYTHONPATH="$SOURCE" "$PYTHON_BIN" -m docforge.cli install --source "$SOURCE"

# ── 5. Post-install summary ──────────────────────────────
echo ""
ok "Installation terminée."
echo ""
"$PYTHON_BIN" -c "from docforge.installer.bootstrap import path_hint; print('  '+path_hint())"
echo ""
echo "Vérifiez :"
echo "  docforge --version"
echo "  docforge doctor"
