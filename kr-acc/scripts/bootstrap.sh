#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

# Copy .env from example if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env from .env.example — edit it to add your ASSEMBLY_API_KEY"
fi

# Build and start all services
docker compose up --build -d

echo ""
echo "kr-acc is running:"
echo "  Frontend: http://localhost:5173"
echo "  Backend:  http://localhost:8000"
echo "  Health:   http://localhost:8000/health"
echo "  Database: localhost:5432"
