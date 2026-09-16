#!/bin/sh
# Compatibility shortcut; Make is the single entry point for lifecycle commands.
set -eu
cd "$(dirname "$0")"
if [ "$#" -eq 0 ]; then
    exec make demo
fi
if [ "$#" -eq 1 ] && [ "$1" = "--reset" ]; then
    exec make reset
fi
echo "Use make demo, make restart, or make reset." >&2
exit 2
