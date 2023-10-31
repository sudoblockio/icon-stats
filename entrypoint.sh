#! /usr/bin/env bash

set -e

if [ "$1" = "streaming" ]; then
  echo "Migrating backend..."
  cd icon_stats
  alembic upgrade head
  echo "Starting streaming..."
  python main_streaming.py "$2"
elif [ "$1" = "cron" ]; then
  echo "Migrating backend..."
  cd icon_stats
  alembic upgrade head
  echo "Starting cron..."
  python main_cron.py
elif [ "$1" = "api" ]; then
  echo "Starting API..."
  python icon_stats/main_api.py
else
  echo "No args specified - exiting..."
fi
