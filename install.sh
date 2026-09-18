#!/usr/bin/env bash
# DocForge installer (POSIX).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

echo "── DocForge installer ──"

if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 requis." >&2
    exit 1
fi

python3 -m pip install --user -r requirements.txt || {
    echo "Installation des dépendances Python échouée." >&2
    exit 2
}

chmod +x ./bin/docforge ./docforge_cli.py 2>/dev/null || true

python3 -m docforge.cli init
python3 -m docforge.cli doctor

echo ""
echo "DocForge est installé. Ajoutez-le au PATH si vous le souhaitez :"
echo "  export PATH=\"$HERE/bin:\$PATH\""
echo ""
echo "Puis lancez :"
echo "  docforge run"
