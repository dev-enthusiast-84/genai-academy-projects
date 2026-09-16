#!/bin/sh
# Launch the current Recall dashboard and its three connected customer apps.
set -eu
cd "$(dirname "$0")"
if [ -x .venv/bin/python ]; then
    exec .venv/bin/python run_demo.py "$@"
fi
exec python3 run_demo.py "$@"
