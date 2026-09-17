#!/usr/bin/env bash
# ============================================================
# run.sh — Heartbeat for the agentic document processing loop
#
# Usage:
#   ./run.sh               # Run one step
#   ./run.sh status        # Show status
#   ./run.sh run           # Run one step
#   ./run.sh run --steps 5 # Run up to 5 steps
#   ./run.sh resume        # Resume from last state
#   ./run.sh reset --force # Reset workflow
#   ./run.sh validate      # Validate structure
#   ./run.sh loop          # Continuous heartbeat (run until DONE/BLOCKED)
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Ensure logs/ and state/ exist
mkdir -p logs state

LOOP_PY="scripts/loop.py"

# ── Colours ──
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $*"; }
err() { echo -e "${RED}[$(date '+%H:%M:%S')] ERROR:${NC} $*" >&2; }
ok()  { echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $*"; }

# ── Dependency check ──
check_deps() {
    if ! command -v python3 &>/dev/null; then
        err "python3 not found"
        exit 1
    fi
    python3 -c "import docx, yaml, lxml" 2>/dev/null || {
        err "Missing Python dependencies. Run: pip3 install -r requirements.txt"
        exit 1
    }
}

# ── Commands ──
cmd_status() {
    python3 "$LOOP_PY" status
}

cmd_run() {
    python3 "$LOOP_PY" run "$@"
}

cmd_resume() {
    python3 "$LOOP_PY" resume "$@"
}

cmd_reset() {
    python3 "$LOOP_PY" reset "$@"
}

cmd_validate() {
    python3 "$LOOP_PY" validate "$@"
}

cmd_loop() {
    # Continuous heartbeat: run steps until DONE, BLOCKED, FAILED,
    # or WAITING_FOR_HUMAN_VALIDATION
    local max_cycles="${1:-100}"
    local delay="${2:-5}"
    local cycle=0

    log "Starting heartbeat loop (max $max_cycles cycles, ${delay}s delay)"

    while [ $cycle -lt $max_cycles ]; do
        cycle=$((cycle + 1))

        # Read current phase
        local phase
        phase=$(python3 -c "
import json, pathlib
s = pathlib.Path('state/loop_state.json')
if s.exists():
    d = json.loads(s.read_text())
    print(d.get('current_phase', 'INIT'))
else:
    print('INIT')
" 2>/dev/null || echo "INIT")

        # Terminal states
        case "$phase" in
            DONE)
                ok "Workflow DONE ✓"
                return 0
                ;;
            BLOCKED)
                err "Workflow BLOCKED — manual intervention required"
                cmd_status
                return 1
                ;;
            FAILED)
                err "Workflow FAILED"
                cmd_status
                return 1
                ;;
            WAITING_FOR_HUMAN_VALIDATION)
                log "${YELLOW}Waiting for human validation of structure proposal${NC}"
                log "Review: work/inspection/structure_proposal.md"
                log "Then run: ./run.sh validate"
                return 0
                ;;
        esac

        # Check for agent_action — this means Claude needs to act
        local agent_action
        agent_action=$(python3 -c "
import json, pathlib
s = pathlib.Path('state/loop_state.json')
if s.exists():
    d = json.loads(s.read_text())
    print(d.get('agent_action', ''))
else:
    print('')
" 2>/dev/null || echo "")

        if [ -n "$agent_action" ]; then
            log "${YELLOW}Agent action required: $agent_action${NC}"
            log "Phase: $phase"
            return 0
        fi

        log "Cycle $cycle/$max_cycles — Phase: $phase"
        python3 "$LOOP_PY" run --steps 1

        sleep "$delay"
    done

    err "Max cycles reached ($max_cycles)"
    cmd_status
    return 1
}

# ── Main ──
check_deps

CMD="${1:-status}"
shift || true

case "$CMD" in
    status)   cmd_status ;;
    run)      cmd_run "$@" ;;
    resume)   cmd_resume "$@" ;;
    reset)    cmd_reset "$@" ;;
    validate) cmd_validate "$@" ;;
    loop)     cmd_loop "$@" ;;
    inspect)  python3 "$LOOP_PY" inspect "$@" ;;
    analyze)  python3 "$LOOP_PY" analyze "$@" ;;
    assemble) python3 "$LOOP_PY" assemble "$@" ;;
    export)   python3 "$LOOP_PY" export "$@" ;;
    report)   python3 "$LOOP_PY" report "$@" ;;
    help|--help|-h)
        echo "Usage: $0 {status|run|resume|reset|validate|loop|inspect|analyze|assemble|export|report|help}"
        echo ""
        echo "  status    Show current workflow state"
        echo "  run       Run one step (--steps N for multiple)"
        echo "  resume    Resume from last state"
        echo "  reset     Reset workflow (--force required)"
        echo "  validate  Validate structure proposal"
        echo "  loop      Run continuous heartbeat until terminal state"
        echo "  inspect   Run document inspection"
        echo "  analyze   Run structure analysis"
        echo "  assemble  Assemble chapters"
        echo "  export    Export DOCX + PDF"
        echo "  report    Generate final report"
        ;;
    *)
        err "Unknown command: $CMD"
        echo "Run: $0 help"
        exit 1
        ;;
esac
