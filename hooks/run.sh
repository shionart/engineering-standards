#!/bin/sh
# Runs hook.py with a working Python 3.10+ interpreter. Usage: run.sh <mode>
# If no suitable Python exists, exit 0 silently: a broken hook must never lock the tools.
# hook.py's own exit code is passed through (2 blocks the tool call).
dir=$(dirname "$0")/gate
for py in python3 python; do
  if "$py" -c 'import sys; sys.exit(sys.version_info < (3, 10))' >/dev/null 2>&1; then
    exec "$py" "$dir/hook.py" "$@"
  fi
done
exit 0
