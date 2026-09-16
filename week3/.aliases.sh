#!/bin/bash
# Recall Demo - Shell Aliases
# Add to your ~/.bashrc or ~/.zshrc:
#   source /path/to/week3/.aliases.sh

RECALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Makefile aliases
alias recall-demo="cd $RECALL_DIR && make demo"
alias recall-start="cd $RECALL_DIR && make start"
alias recall-stop="cd $RECALL_DIR && make stop"
alias recall-reset="cd $RECALL_DIR && make reset"

# App shortcuts (open in browser)
alias recall-open="cd $RECALL_DIR && make recall"
alias portal-open="cd $RECALL_DIR && make portal"
alias booking-open="cd $RECALL_DIR && make booking"
alias offers-open="cd $RECALL_DIR && make offers"
alias recall-open-all="cd $RECALL_DIR && make open-all"

# Helper function - open app and optionally start demo
function recall() {
    case "$1" in
        start|demo)
            cd "$RECALL_DIR" && make demo
            ;;
        stop|kill)
            cd "$RECALL_DIR" && make stop
            ;;
        reset)
            cd "$RECALL_DIR" && make reset
            ;;
        portal|club)
            cd "$RECALL_DIR" && make portal
            ;;
        booking|class)
            cd "$RECALL_DIR" && make booking
            ;;
        offers|member)
            cd "$RECALL_DIR" && make offers
            ;;
        dashboard|app)
            cd "$RECALL_DIR" && make recall
            ;;
        all)
            cd "$RECALL_DIR" && make open-all
            ;;
        help|--help|-h)
            cat << 'EOF'
Recall Demo - Shortcut Commands

Usage:
  recall <command>

Commands:
  start/demo       Start all 4 apps + LiteLLM
  stop             Stop all processes
  reset            Reset demo data

  dashboard/app    Open Recall Dashboard (8501)
  portal/club      Open Club Portal (8101)
  booking/class    Open Class Booking (8102)
  offers/member    Open Member Offers (8103)
  all              Open all 4 apps

Shell aliases:
  recall-demo      = make demo
  recall-start     = make start
  recall-stop      = make stop
  recall-open      = open Recall Dashboard
  portal-open      = open Club Portal
  booking-open     = open Class Booking
  offers-open      = open Member Offers
  recall-open-all  = open all 4 apps

EOF
            ;;
        *)
            echo "Unknown command: $1"
            echo "Run 'recall help' for available commands"
            ;;
    esac
}

echo "✓ Recall aliases loaded. Run 'recall help' for commands."
