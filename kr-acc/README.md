# kr-acc — Korean Politician Open Graph

Civic tech transparency platform that aggregates Korean National Assembly data into a unified graph database.

## Quick Start

```bash
cp .env.example .env
# Edit .env to add your ASSEMBLY_API_KEY from open.assembly.go.kr

./scripts/bootstrap.sh
```

Services:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Health check**: http://localhost:8000/health

## Development

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

## Tech Stack

- **Database**: PostgreSQL 16 + Apache AGE (graph extension)
- **Backend**: FastAPI (Python 3.12+, async)
- **ETL**: Prefect 3.x
- **Frontend**: React 19 + Vite + TypeScript + D3.js

## Data Source

[열린국회정보 API](https://open.assembly.go.kr) — legally public National Assembly data.

## License

MIT
