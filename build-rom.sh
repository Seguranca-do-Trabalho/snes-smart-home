#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"

if [[ -z "${PVSNESLIB_HOME:-}" && -d "/home/forg3/tools/pvsneslib" ]]; then
  export PVSNESLIB_HOME="/home/forg3/tools/pvsneslib"
fi

if [[ -n "${PVSNESLIB_HOME:-}" ]]; then
  export PATH="$PVSNESLIB_HOME/devkitsnes/bin:$PVSNESLIB_HOME/devkitsnes/tools:$PATH"
  cd "$ROOT/snes"
  make
else
  echo "PVSNESLIB_HOME is not set." >&2
  exit 2
fi
