#!/usr/bin/env bash
set -euo pipefail

: "${database_url:?database_url must be set}"

MAX_RETRIES=30
SLEEP=2
i=0

echo "Waiting for DB and running migrations..."
until uv run piccolo migrations forwards all; do
  i=$((i+1))
  if [ "$i" -ge "$MAX_RETRIES" ]; then
    exit 1
  fi
  sleep $SLEEP
done

exec "$@"
