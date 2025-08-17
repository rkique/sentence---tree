#!/usr/bin/env bash
set -euo pipefail

FLASK_PORT=${FLASK_PORT:-5001}

cleanup() {
  echo "container: cleaning up..."
  [ -n "${BDEV_PID:-}" ] && kill "$BDEV_PID" 2>/dev/null || true
  [ -n "${DEV_PID:-}" ] && kill "$DEV_PID" 2>/dev/null || true
  lsof -ti:"$FLASK_PORT" | xargs -r kill -9 || true
}

trap cleanup EXIT INT TERM

# Start backend dev script if present
if [ -x "./bdev.sh" ]; then
  echo "container: starting bdev.sh"
  ./bdev.sh &
  BDEV_PID=$!
else
  echo "container: bdev.sh not found or not executable"
fi

# Start frontend dev script if present
if [ -x "./dev.sh" ]; then
  echo "container: starting dev.sh"
  ./dev.sh &
  DEV_PID=$!
else
  echo "container: dev.sh not found or not executable"
fi

PIDS=""
[ -n "${BDEV_PID:-}" ] && PIDS="$PIDS $BDEV_PID"
[ -n "${DEV_PID:-}" ] && PIDS="$PIDS $DEV_PID"

if [ -z "$PIDS" ]; then
  echo "container: no processes started, exiting"
  exit 1
fi

wait $PIDS