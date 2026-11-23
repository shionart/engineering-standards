#!/usr/bin/env bash
# Copy the fixture workspace next to the agent's working directory (cwd of this script).
set -euo pipefail
cp -r "$(dirname "$0")/fixture/." .
