#!/bin/bash

set -e

cd "$(dirname "$0")/.." || exit 1

/usr/local/bin/docker compose up \
  --force-recreate \
  --abort-on-container-exit \
  --no-deps \
  producer_history_strava dbt strava_sender

echo "$(date): Daily pipeline execution completed"