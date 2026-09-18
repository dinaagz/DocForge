#!/usr/bin/env bash
# ============================================================
# run.sh — wrapper LEGACY vers `docforge`.
#
# Cette interface est conservée UNIQUEMENT pour la
# rétro-compatibilité pendant la migration Loop → DocForge.
# Nouveaux utilisateurs : utilisez `bin/docforge` (ou `docforge`
# une fois ajouté au PATH) directement.
# ============================================================
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export DOCFORGE_ROOT="${DOCFORGE_ROOT:-$HERE}"

CMD="${1:-status}"
shift || true

case "$CMD" in
    status|run|resume|reset|report|providers|workers|audit|doctor|init|pause|stop)
        exec python3 -m docforge.cli "$CMD" "$@"
        ;;
    validate)
        # Compatibilité : la validation humaine est désormais automatique.
        # Le workflow ne s'arrête plus pour attendre une approbation.
        echo "[LEGACY] La validation humaine est désormais automatique dans DocForge."
        echo "         Le workflow s'exécute jusqu'à un état terminal sans pause."
        exec python3 -m docforge.cli status
        ;;
    loop)
        echo "[LEGACY] 'loop' remplacé par 'run'. Utilisation de docforge run."
        exec python3 -m docforge.cli run "$@"
        ;;
    inspect|analyze|assemble|export)
        echo "[LEGACY] Sous-commande dépréciée. Utilisez 'docforge run' pour l'exécution complète."
        exec python3 scripts/loop.py "$CMD" "$@"
        ;;
    # Document Craft commands
    craft)         python3 scripts/loop.py craft "$@" ;;
    taste)         python3 scripts/loop.py taste "$@" ;;
    typography)    python3 scripts/loop.py typography "$@" ;;
    composition)   python3 scripts/loop.py composition "$@" ;;
    rhythm)        python3 scripts/loop.py rhythm "$@" ;;
    polish)        python3 scripts/loop.py polish "$@" ;;
    humanize)      python3 scripts/loop.py humanize "$@" ;;
    visual-audit)  python3 scripts/loop.py visual-audit "$@" ;;
    help|--help|-h)
        echo "Wrapper LEGACY. Utilisez de préférence :"
        echo "  bin/docforge run"
        echo "  bin/docforge status"
        echo "  bin/docforge report"
        echo "  bin/docforge doctor"
        echo ""
        echo "  Document Craft:"
        echo "  ./run.sh craft        Pipeline complet de qualité éditoriale"
        echo "  ./run.sh taste        Analyse du goût éditorial"
        echo "  ./run.sh typography   Optimisation typographique"
        echo "  ./run.sh composition  Analyse de la composition des pages"
        echo "  ./run.sh rhythm       Analyse du rythme documentaire"
        echo "  ./run.sh polish       Dernière passe de finition"
        echo "  ./run.sh humanize     Réduire les signes de génération mécanique"
        echo "  ./run.sh visual-audit Export PDF et audit visuel"
        ;;
    *)
        echo "Commande inconnue : $CMD"
        echo "Voir : ./run.sh help  ou  bin/docforge --help"
        exit 1
        ;;
esac
