#!/bin/sh
# Runs hook.py with a working Python 3.10+ interpreter. Usage: run.sh <mode>
# If no suitable Python exists, exit 0: a broken hook must never lock the tools. Only the SessionStart
# mode (reset) says so, as one line of session context; every other mode stays silent.
# hook.py's own exit code is passed through (2 blocks the tool call).
case $0 in */*) dir=${0%/*}/gate ;; *) dir=gate ;; esac  # no dirname: it may be missing from PATH
for py in python3 python; do
  if "$py" -c 'import sys; sys.exit(sys.version_info < (3, 10))' >/dev/null 2>&1; then
    exec "$py" "$dir/hook.py" "$@"
  fi
done
if [ "$1" = reset ]; then
  echo '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"engineering-standards gate is inactive: Python 3.10+ not found."}}'
fi
exit 0
