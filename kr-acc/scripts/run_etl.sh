#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Running ETL sync_all flow..."
docker compose exec etl-worker python -m flows.sync_all
